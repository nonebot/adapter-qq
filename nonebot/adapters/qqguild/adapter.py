import sys
import json
import asyncio
from typing import Any, Dict, List, Tuple, Union, Optional

from pydantic import parse_raw_as
from nonebot.typing import overrides
from nonebot.utils import escape_tag
from nonebot.exception import WebSocketClosed
from nonebot.drivers import URL, Driver, Request, WebSocket, ForwardDriver

from nonebot.adapters import Adapter as BaseAdapter

from .bot import Bot
from .utils import log
from .config import Config, BotInfo
from .event import Event, EventType
from .model import User, Guild, Gateway, GuildRoles, GatewayWithShards
from .payload import (
    Hello,
    Opcode,
    Resume,
    Payload,
    Dispatch,
    Identify,
    Heartbeat,
    Reconnect,
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
        self.connections: Dict[str, WebSocket] = {}
        self.api_base: Optional[URL] = None
        self.setup()

    @classmethod
    @overrides(BaseAdapter)
    def get_name(cls) -> str:
        return "QQ Guild"

    def setup(self) -> None:
        if not isinstance(self.driver, ForwardDriver):
            raise RuntimeError(
                f"Current driver {self.config.driver} don't support forward connections!"
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
            gateway_info = await bot.get_gateway_with_shards()
            ws_url = URL(gateway_info.url)
        except Exception as e:
            log(
                "ERROR",
                "<r><bg #f8bbd0>Failed to get gateway info.</bg #f8bbd0></r>",
                e,
            )
            return

        if gateway_info.session_start_limit.remaining <= 0:
            log(
                "ERROR",
                "<r><bg #f8bbd0>Failed to establish connection to QQ Guild "
                "because of session start limit.</bg #f8bbd0></r>\n"
                f"{escape_tag(repr(gateway_info))}",
            )
            return

        if bot_info.current_shard is not None:
            self.tasks.append(
                asyncio.create_task(
                    self._forward_ws(bot, ws_url, bot_info.current_shard)
                )
            )
            return

        for i in range(gateway_info.shards):
            self.tasks.append(
                asyncio.create_task(
                    self._forward_ws(bot, ws_url, (i, gateway_info.shards))
                )
            )
            await asyncio.sleep(gateway_info.session_start_limit.max_concurrency)

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
                    self.connections[bot.self_id] = ws

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
                            payload = Identify(
                                data={
                                    "token": self.get_authorization(bot.bot_info),
                                    "intents": bot.bot_info.current_intent.to_int(),
                                    "shard": list(shard),
                                    "properties": {
                                        "$os": sys.platform,
                                        "$sdk": "NoneBot2",
                                    },
                                },
                            )
                        else:
                            payload = Resume(
                                data={
                                    "token": self.get_authorization(bot.bot_info),
                                    "session_id": bot.session_id,
                                    "seq": bot.sequence,
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

                        try:
                            payload = await self.receive_payload(ws)
                            assert (
                                isinstance(payload, Dispatch)
                                and payload.type == EventType.READY
                            ), f"Received unexpected payload: {payload!r}"
                            bot.session_id = payload.data["session_id"]
                            bot.self_info = payload.data["user"]
                            bot.sequence = payload.sequence
                        except Exception as e:
                            log(
                                "ERROR",
                                "<r><bg #f8bbd0>Error while receiving server ready event</bg #f8bbd0></r>",
                                e,
                            )
                            await asyncio.sleep(RECONNECT_INTERVAL)
                            continue

                        self.bot_connect(bot)
                        log(
                            "INFO",
                            f"<y>Bot {escape_tag(str(bot.self_info))}</y> connected",
                        )
                        # start heartbeat
                        heartbeat_task = asyncio.create_task(
                            self._heartbeat(bot, heartbeat_interval)
                        )
                        while True:
                            payload = await self.receive_payload(ws)
                            print(payload)
                            if isinstance(payload, Dispatch):
                                bot.sequence = payload.sequence
                                event = self.payload_to_event(payload)
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
                            else:
                                log(
                                    "WARNING",
                                    f"Unknown payload from server: {escape_tag(str(payload.dict()))}",
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
                        self.connections.pop(bot.self_id, None)
                        self.bot_disconnect(bot)

            except Exception as e:
                log(
                    "ERROR",
                    "<r><bg #f8bbd0>Error while setup websocket to "
                    f"{escape_tag(str(ws_url))}. Trying to reconnect...</bg #f8bbd0></r>",
                    e,
                )

            await asyncio.sleep(RECONNECT_INTERVAL)

    async def _heartbeat(self, bot: Bot, heartbeat_interval: int):
        while True:
            ws = self.connections[bot.self_id]
            if bot.has_sequence:
                log("TRACE", f"Heartbeat {bot.sequence}")
                payload = Heartbeat(data=bot.sequence)
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
        return f"Bot {bot.app_id}.{bot.app_token}"

    async def receive_payload(self, ws: WebSocket) -> Payload:
        return parse_raw_as(
            Union[Dispatch, Reconnect, InvalidSession, Hello, HeartbeatAck, Payload],
            await ws.receive(),
        )

    @classmethod
    def payload_to_event(cls, payload: Payload) -> Event:
        ...

    @overrides(BaseAdapter)
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        api_handler = self.api_handlers.get(api, None)
        if api_handler is None:
            raise ValueError(f"Unknown API: {api}")
        return await api_handler(self, bot, **data)

    async def _get_guild(self, bot: Bot, guild_id: str) -> Guild:
        request = Request(
            "GET",
            self.get_api_base() / f"guilds/{guild_id}",
            headers={"Authorization": self.get_authorization(bot.bot_info)},
        )
        data = await self.request(request)
        assert data.content is not None
        return Guild.parse_raw(data.content)

    async def _get_guild_roles(self, bot: Bot, guild_id: str) -> GuildRoles:
        request = Request(
            "GET",
            self.get_api_base() / f"guilds/{guild_id}/roles",
            headers={"Authorization": self.get_authorization(bot.bot_info)},
        )
        data = await self.request(request)
        assert data.content is not None
        return GuildRoles.parse_raw(data.content)

    async def _get_gateway(self, bot: Bot) -> Gateway:
        request = Request(
            "GET",
            self.get_api_base() / "gateway",
            headers={"Authorization": self.get_authorization(bot.bot_info)},
        )
        data = await self.request(request)
        assert data.content is not None
        return Gateway.parse_raw(data.content)

    async def _get_gateway_with_shards(self, bot: Bot) -> GatewayWithShards:
        request = Request(
            "GET",
            self.get_api_base() / "gateway" / "bot",
            headers={"Authorization": self.get_authorization(bot.bot_info)},
        )
        data = await self.request(request)
        assert data.content is not None
        return GatewayWithShards.parse_raw(data.content)

    api_handlers = {
        # Guild API
        "get_guild": _get_guild,
        # Guild Role API
        "get_guild_roles": _get_guild_roles,
        # WebSocket API
        "get_gateway": _get_gateway,
        "get_gateway_with_shards": _get_gateway_with_shards,
    }
