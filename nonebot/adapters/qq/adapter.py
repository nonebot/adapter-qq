import sys
import asyncio
from typing_extensions import override
from typing import Any, List, Tuple, Literal, Optional

from pydantic import parse_raw_as
from nonebot.utils import escape_tag
from nonebot.exception import WebSocketClosed
from nonebot.drivers import (
    URL,
    Driver,
    Request,
    WebSocket,
    HTTPClientMixin,
    WebSocketClientMixin,
)

from nonebot.adapters import Adapter as BaseAdapter

from .bot import Bot
from .utils import API, log
from .store import audit_result
from .config import Config, BotInfo
from .exception import ApiNotAvailable
from .event import EVENT_CLASSES, Event, ReadyEvent, MessageAuditEvent
from .models import (
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
    @override
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)

        self.qq_config: Config = Config(**self.config.dict())

        self.tasks: List["asyncio.Task"] = []
        self.setup()

    @classmethod
    @override
    def get_name(cls) -> str:
        return "QQ"

    def setup(self) -> None:
        if not isinstance(self.driver, HTTPClientMixin):
            raise RuntimeError(
                f"Current driver {self.config.driver} does not support "
                "http client requests! "
                "QQ Adapter need a HTTPClient Driver to work."
            )
        if not isinstance(self.driver, WebSocketClientMixin):
            raise RuntimeError(
                f"Current driver {self.config.driver} does not support "
                "websocket client! "
                "QQ Adapter need a WebSocketClient Driver to work."
            )
        self.driver.on_startup(self.startup)
        self.driver.on_shutdown(self.shutdown)

    async def startup(self) -> None:
        log(
            "DEBUG",
            ("QQ run in sandbox mode: " f"<y>{self.qq_config.qq_is_sandbox}</y>"),
        )

        try:
            api_base = self.get_api_base()
        except Exception as e:
            log("ERROR", "Failed to parse QQ api base url", e)
            raise

        log("DEBUG", f"QQ api base url: <y>{escape_tag(str(api_base))}</y>")

        for bot in self.qq_config.qq_bots:
            self.tasks.append(asyncio.create_task(self.run_bot(bot)))

    async def shutdown(self) -> None:
        for task in self.tasks:
            if not task.done():
                task.cancel()

        await asyncio.gather(
            *(asyncio.wait_for(task, timeout=10) for task in self.tasks),
            return_exceptions=True,
        )

    async def run_bot(self, bot_info: BotInfo) -> None:
        bot = Bot(self, bot_info.id, bot_info)

        # get sharded gateway url
        try:
            gateway_info = await bot.shard_url_get()
            ws_url = URL(gateway_info.url)
        except Exception as e:
            log(
                "ERROR",
                "<r><bg #f8bbd0>Failed to get gateway info.</bg #f8bbd0></r>",
                e,
            )
            return

        if (remain := gateway_info.session_start_limit.remaining) and remain <= 0:
            log(
                "ERROR",
                "<r><bg #f8bbd0>Failed to establish connection to QQ "
                "because of session start limit.</bg #f8bbd0></r>\n"
                f"{escape_tag(repr(gateway_info))}",
            )
            return

        # start connection in single shard mode
        if bot_info.shard is not None:
            self.tasks.append(
                asyncio.create_task(self._forward_ws(bot, ws_url, bot_info.shard))
            )
            return

        # start connection in sharding mode
        shards = gateway_info.shards or 1
        for i in range(shards):
            self.tasks.append(
                asyncio.create_task(self._forward_ws(bot, ws_url, (i, shards)))
            )
            # wait for session start concurrency limit
            await asyncio.sleep(gateway_info.session_start_limit.max_concurrency or 1)

    async def _forward_ws(self, bot: Bot, ws_url: URL, shard: Tuple[int, int]) -> None:
        # ws setup request
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
                        (
                            "WebSocket Connection to "
                            f"{escape_tag(str(ws_url))} established"
                        ),
                    )

                    try:
                        # hello
                        heartbeat_interval = await self._hello(bot, ws)
                        if heartbeat_interval is None:
                            await asyncio.sleep(RECONNECT_INTERVAL)
                            continue

                        # identify/resume
                        result = await self._authenticate(bot, ws, shard)
                        if not result:
                            await asyncio.sleep(RECONNECT_INTERVAL)
                            continue

                        # start heartbeat
                        heartbeat_task = asyncio.create_task(
                            self._heartbeat(bot, ws, heartbeat_interval)
                        )

                        # process events
                        await self._loop(bot, ws)
                    except WebSocketClosed as e:
                        log(
                            "ERROR",
                            "<r><bg #f8bbd0>WebSocket Closed</bg #f8bbd0></r>",
                            e,
                        )
                    except Exception as e:
                        log(
                            "ERROR",
                            (
                                "<r><bg #f8bbd0>"
                                "Error while process data from websocket "
                                f"{escape_tag(str(ws_url))}. Trying to reconnect..."
                                "</bg #f8bbd0></r>"
                            ),
                            e,
                        )
                    finally:
                        if heartbeat_task:
                            heartbeat_task.cancel()
                            heartbeat_task = None
                        if bot.self_id in self.bots:
                            self.bot_disconnect(bot)

            except Exception as e:
                log(
                    "ERROR",
                    (
                        "<r><bg #f8bbd0>"
                        "Error while setup websocket to "
                        f"{escape_tag(str(ws_url))}. Trying to reconnect..."
                        "</bg #f8bbd0></r>"
                    ),
                    e,
                )

            await asyncio.sleep(RECONNECT_INTERVAL)

    async def _hello(self, bot: Bot, ws: WebSocket) -> Optional[int]:
        """接收并处理服务器的 Hello 事件"""
        try:
            payload = await self.receive_payload(bot, ws)
            assert isinstance(
                payload, Hello
            ), f"Received unexpected payload: {payload!r}"
            return payload.data.heartbeat_interval
        except Exception as e:
            log(
                "ERROR",
                (
                    "<r><bg #f8bbd0>"
                    "Error while receiving server hello event"
                    "</bg #f8bbd0></r>"
                ),
                e,
            )

    async def _authenticate(
        self, bot: Bot, ws: WebSocket, shard: Tuple[int, int]
    ) -> Optional[Literal[True]]:
        """鉴权连接"""
        if not bot.ready:
            payload = Identify.parse_obj(
                {
                    "data": {
                        "token": await bot._get_authorization_header(),
                        "intents": bot.bot_info.intent.to_int(),
                        "shard": shard,
                        "properties": {
                            "$os": sys.platform,
                            "$language": f"python {sys.version}",
                            "$sdk": "NoneBot2",
                        },
                    },
                }
            )
        else:
            payload = Resume.parse_obj(
                {
                    "data": {
                        "token": await bot._get_authorization_header(),
                        "session_id": bot.session_id,
                        "seq": bot.sequence,
                    }
                }
            )

        try:
            await ws.send(self.payload_to_json(payload))
        except Exception as e:
            log(
                "ERROR",
                "<r><bg #f8bbd0>Error while sending "
                + ("Identify" if isinstance(payload, Identify) else "Resume")
                + " event</bg #f8bbd0></r>",
                e,
            )
            return

        ready_event = None
        if not bot.ready:
            # https://bot.q.qq.com/wiki/develop/api/gateway/reference.html#_2-%E9%89%B4%E6%9D%83%E8%BF%9E%E6%8E%A5
            # 鉴权成功之后，后台会下发一个 Ready Event
            payload = await self.receive_payload(bot, ws)
            if isinstance(payload, InvalidSession):
                log(
                    "WARNING",
                    "Received invalid session event from server. Try to reconnect...",
                )
                return
            elif not isinstance(payload, Dispatch):
                log(
                    "ERROR",
                    "Received unexpected payload while authenticating: "
                    f"{escape_tag(repr(payload))}",
                )
                return

            ready_event = self.payload_to_event(payload)
            if not isinstance(ready_event, ReadyEvent):
                log(
                    "ERROR",
                    "Received unexpected event while authenticating: "
                    f"{escape_tag(repr(ready_event))}",
                )
                return

            bot.on_ready(ready_event)

        # only connect for single shard
        if bot.self_id not in self.bots:
            self.bot_connect(bot)
            log(
                "INFO",
                f"<y>Bot {escape_tag(bot.self_id)}</y> connected",
            )

        if ready_event:
            asyncio.create_task(bot.handle_event(ready_event))

        return True

    async def _heartbeat(self, bot: Bot, ws: WebSocket, heartbeat_interval: int):
        """心跳"""
        while True:
            if bot.ready:
                log("TRACE", f"Heartbeat {bot.sequence}")
                payload = Heartbeat.parse_obj({"data": bot.sequence})
                try:
                    await ws.send(self.payload_to_json(payload))
                except Exception as e:
                    log("WARNING", "Error while sending heartbeat, Ignored!", e)
            await asyncio.sleep(heartbeat_interval / 1000)

    async def _loop(self, bot: Bot, ws: WebSocket):
        """接收并处理事件"""
        while True:
            payload = await self.receive_payload(bot, ws)
            log(
                "TRACE",
                f"Received payload: {escape_tag(repr(payload))}",
            )
            if isinstance(payload, Dispatch):
                try:
                    event = self.payload_to_event(payload)
                except Exception as e:
                    log(
                        "WARNING",
                        f"Failed to parse event {escape_tag(repr(payload))}",
                        e,
                    )
                else:
                    if isinstance(event, MessageAuditEvent):
                        audit_result.add_result(event)
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
                bot.reset()
                log(
                    "ERROR",
                    "Received invalid session event from server. Try to reconnect...",
                )
                break
            else:
                log(
                    "WARNING",
                    f"Unknown payload from server: {escape_tag(repr(payload))}",
                )

    def get_auth_base(self) -> URL:
        return URL(self.qq_config.qq_auth_base)

    def get_api_base(self) -> URL:
        if self.qq_config.qq_is_sandbox:
            return URL(self.qq_config.qq_sandbox_api_base)
        else:
            return URL(self.qq_config.qq_api_base)

    @staticmethod
    async def receive_payload(bot: Bot, ws: WebSocket) -> Payload:
        payload = parse_raw_as(PayloadType, await ws.receive())
        if isinstance(payload, Dispatch):
            bot.on_dispatch(payload)
        return payload

    @staticmethod
    def payload_to_json(payload: Payload) -> str:
        return payload.__config__.json_dumps(
            payload.dict(), default=payload.__json_encoder__
        )

    @staticmethod
    def payload_to_event(payload: Dispatch) -> Event:
        EventClass = EVENT_CLASSES.get(payload.type, None)
        if EventClass is None:
            log("WARNING", f"Unknown payload type: {payload.type}")
            event = Event.parse_obj(payload.data)
            event.__type__ = payload.type  # type: ignore
            return event
        return EventClass.parse_obj(payload.data)

    @override
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        log("DEBUG", f"Bot {bot.bot_info.id} calling API <y>{api}</y>")
        api_handler: Optional[API] = getattr(bot.__class__, api, None)
        if api_handler is None:
            raise ApiNotAvailable
        return await api_handler(bot, **data)
