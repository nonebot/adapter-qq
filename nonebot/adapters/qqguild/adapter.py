import sys
import json
import asyncio
from typing import Any, List, Tuple, Optional

from pydantic import parse_raw_as
from nonebot.typing import overrides
from nonebot.utils import escape_tag
from nonebot.exception import WebSocketClosed
from nonebot.drivers import URL, Driver, Request, WebSocket, ForwardDriver

from nonebot.adapters import Adapter as BaseAdapter
from nonebot.adapters.qqguild.exception import ApiNotAvailable

from .bot import Bot
from .utils import log
from .api import API_HANDLERS
from .config import Config, BotInfo
from .event import Event, event_classes
from .payload import (
    Hello,
    Resume,
    Payload,
    Dispatch,
    Identify,
    Heartbeat,
    Reconnect,
    PayloadType,
    HeartbeatAck,
    InvalidSession,
)

RECONNECT_INTERVAL = 3.0


class Adapter(BaseAdapter):
    @overrides(BaseAdapter)
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        self.qqguild_config: Config = Config(**self.config.dict())
        self.tasks: List["asyncio.Task"] = []
        self.api_base: Optional[URL] = None
        self.setup()

    @classmethod
    @overrides(BaseAdapter)
    def get_name(cls) -> str:
        return "QQ Guild"

    def setup(self) -> None:
        if not isinstance(self.driver, ForwardDriver):
            raise RuntimeError(
                f"Current driver {self.config.driver} doesn't support forward connections!"
                "QQ Guild Adapter need a ForwardDriver to work."
            )
        self.driver.on_startup(self.startup)
        self.driver.on_shutdown(self.shutdown)

    async def startup(self) -> None:
        log(
            "DEBUG",
            f"QQ Guild run in sandbox mode: <y>{self.qqguild_config.qqguild_is_sandbox}</y>",
        )

        try:
            self.api_base = self.get_api_base()
        except Exception as e:
            log("ERROR", f"Failed to parse QQ Guild api base url", e)
            raise

        log("DEBUG", f"QQ Guild api base url: <y>{escape_tag(str(self.api_base))}</y>")

        for bot in self.qqguild_config.qqguild_bots:
            self.tasks.append(asyncio.create_task(self.run_bot(bot)))

    async def shutdown(self) -> None:
        for task in self.tasks:
            if not task.done():
                task.cancel()

    async def run_bot(self, bot_info: BotInfo) -> None:
        bot = Bot(self, bot_info)
        try:
            gateway_info = await bot.shard_url_get()
            if not gateway_info.url:
                raise ValueError("Failed to get gateway url")
            ws_url = URL(gateway_info.url)
        except Exception as e:
            log(
                "ERROR",
                "<r><bg #f8bbd0>Failed to get gateway info.</bg #f8bbd0></r>",
                e,
            )
            return

        remain = (
            gateway_info.session_start_limit
            and gateway_info.session_start_limit.remaining
        )
        if remain and remain <= 0:
            log(
                "ERROR",
                "<r><bg #f8bbd0>Failed to establish connection to QQ Guild "
                "because of session start limit.</bg #f8bbd0></r>\n"
                f"{escape_tag(repr(gateway_info))}",
            )
            return

        if bot_info.shard is not None:
            self.tasks.append(
                asyncio.create_task(self._forward_ws(bot, ws_url, bot_info.shard))
            )
            return

        shards = gateway_info.shards or 1
        for i in range(shards):
            self.tasks.append(
                asyncio.create_task(self._forward_ws(bot, ws_url, (i, shards)))
            )
            await asyncio.sleep(
                gateway_info.session_start_limit
                and gateway_info.session_start_limit.max_concurrency
                or 1
            )

    async def _forward_ws(self, bot: Bot, ws_url: URL, shard: Tuple[int, int]) -> None:
        request = Request(
            "GET",
            ws_url,
            timeout=30.0,
        )
        heartbeat_task: Optional["asyncio.Task"] = None

        while True:
            try:
                async with self.websocket(request) as ws:
                    log(
                        "DEBUG",
                        f"WebSocket Connection to {escape_tag(str(ws_url))} established",
                    )

                    try:

                        try:
                            payload = await self.receive_payload(ws)
                            assert isinstance(
                                payload, Hello
                            ), f"Received unexpected payload: {payload!r}"
                            heartbeat_interval = payload.data.heartbeat_interval
                        except Exception as e:
                            log(
                                "ERROR",
                                "<r><bg #f8bbd0>Error while receiving server hello event</bg #f8bbd0></r>",
                                e,
                            )
                            await asyncio.sleep(RECONNECT_INTERVAL)
                            continue

                        if not bot.ready:
                            payload = Identify.parse_obj(
                                {
                                    "data": {
                                        "token": self.get_authorization(bot.bot_info),
                                        "intents": bot.bot_info.intent.to_int(),
                                        "shard": list(shard),
                                        "properties": {
                                            "$os": sys.platform,
                                            "$sdk": "NoneBot2",
                                        },
                                    },
                                }
                            )
                        else:
                            payload = Resume.parse_obj(
                                {
                                    "data": {
                                        "token": self.get_authorization(bot.bot_info),
                                        "session_id": bot.session_id,
                                        "seq": bot.sequence,
                                    }
                                }
                            )

                        try:
                            await ws.send(json.dumps(payload.dict()))
                        except Exception as e:
                            log(
                                "ERROR",
                                "<r><bg #f8bbd0>Error while sending " + "Identify"
                                if isinstance(payload, Identify)
                                else "Resume" + " event</bg #f8bbd0></r>",
                                e,
                            )
                            await asyncio.sleep(RECONNECT_INTERVAL)
                            continue

                        # only connect for single shard
                        if bot.self_id not in self.bots:
                            self.bot_connect(bot)
                            log(
                                "INFO",
                                f"<y>Bot {escape_tag(bot.self_id)}</y> connected",
                            )
                        # start heartbeat
                        heartbeat_task = asyncio.create_task(
                            self._heartbeat(ws, bot, heartbeat_interval)
                        )
                        while True:
                            payload = await self.receive_payload(ws)
                            log(
                                "TRACE",
                                f"Received payload: {escape_tag(repr(payload))}",
                            )
                            if isinstance(payload, Dispatch):
                                bot.sequence = payload.sequence
                                try:
                                    event = self.payload_to_event(payload)
                                except Exception as e:
                                    log(
                                        "WARNING",
                                        f"Failed to parse event {escape_tag(repr(payload))}",
                                        e,
                                    )
                                else:
                                    asyncio.create_task(bot.handle_event(event))
                            elif isinstance(payload, HeartbeatAck):
                                log("TRACE", "Heartbeat ACK")
                                continue
                            elif isinstance(payload, Reconnect):
                                log(
                                    "WARNING",
                                    "Received reconnect event from server. Try to reconnect...",
                                )
                                break
                            elif isinstance(payload, InvalidSession):
                                bot.clear()
                                log(
                                    "Error",
                                    "Received invalid session event from server. Try to reconnect...",
                                )
                                break
                            else:
                                log(
                                    "WARNING",
                                    f"Unknown payload from server: {escape_tag(repr(payload))}",
                                )
                    except WebSocketClosed as e:
                        log(
                            "ERROR",
                            f"<r><bg #f8bbd0>WebSocket Closed</bg #f8bbd0></r>",
                            e,
                        )
                    except Exception as e:
                        log(
                            "ERROR",
                            "<r><bg #f8bbd0>Error while process data from websocket "
                            f"{escape_tag(str(ws_url))}. Trying to reconnect...</bg #f8bbd0></r>",
                            e,
                        )
                    finally:
                        if heartbeat_task:
                            heartbeat_task.cancel()
                            heartbeat_task = None
                        self.bot_disconnect(bot)

            except Exception as e:
                log(
                    "ERROR",
                    "<r><bg #f8bbd0>Error while setup websocket to "
                    f"{escape_tag(str(ws_url))}. Trying to reconnect...</bg #f8bbd0></r>",
                    e,
                )

            await asyncio.sleep(RECONNECT_INTERVAL)

    async def _heartbeat(self, ws: WebSocket, bot: Bot, heartbeat_interval: int):
        while True:
            if bot.has_sequence:
                log("TRACE", f"Heartbeat {bot.sequence}")
                payload = Heartbeat.parse_obj({"data": bot.sequence})
                try:
                    await ws.send(json.dumps(payload.dict()))
                except Exception:
                    pass
            await asyncio.sleep(heartbeat_interval / 1000)

    def get_api_base(self) -> URL:
        if self.qqguild_config.qqguild_is_sandbox:
            return URL(self.qqguild_config.qqguild_sandbox_api_base)
        else:
            return URL(self.qqguild_config.qqguild_api_base)

    def get_authorization(self, bot: BotInfo) -> str:
        return f"Bot {bot.id}.{bot.token}"

    async def receive_payload(self, ws: WebSocket) -> Payload:
        return parse_raw_as(PayloadType, await ws.receive())

    @classmethod
    def payload_to_event(cls, payload: Dispatch) -> Event:
        EventClass = event_classes.get(payload.type, None)
        if not EventClass:
            raise ValueError(f"Unknown payload type: {payload.type}")
        return EventClass.parse_obj(payload.data)

    @overrides(BaseAdapter)
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        log("DEBUG", f"Calling API <y>{api}</y>")
        api_handler = API_HANDLERS.get(api, None)
        if api_handler is None:
            raise ApiNotAvailable
        return await api_handler(self, bot, **data)
