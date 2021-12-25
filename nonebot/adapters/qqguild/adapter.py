import sys
import asyncio
from typing import Any, List, Union, Optional

from pydantic import parse_raw_as
from nonebot.typing import overrides
from nonebot.utils import escape_tag
from nonebot.drivers import URL, Driver, Request, WebSocket, ForwardDriver

from nonebot.adapters import Adapter as BaseAdapter

from .bot import Bot
from .utils import log
from .event import Event
from .config import Config, BotInfo
from .model import Guild, GuildRoles
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
        bot = Bot(self, bot_info.app_id)
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

        request = Request(
            "GET",
            ws_url,
            timeout=30.0,
        )

        while True:
            try:
                ws = await self.websocket(request)
            except Exception as e:
                log(
                    "ERROR",
                    "<r><bg #f8bbd0>Error while setup websocket to "
                    f"{escape_tag(str(ws_url))}. Trying to reconnect...</bg #f8bbd0></r>",
                    e,
                )
                await asyncio.sleep(RECONNECT_INTERVAL)
                continue

            log(
                "DEBUG",
                f"WebSocket Connection to {escape_tag(str(ws_url))} established",
            )

            try:
                payload = await self.receive_payload(ws)
                assert isinstance(payload, Hello)
                heartbeat_interval = payload.data.heartbeat_interval
            except Exception as e:
                log(
                    "ERROR",
                    "<r><bg #f8bbd0>Error while receiving server hello event</bg #f8bbd0></r>",
                    e,
                )
                try:
                    await ws.close()
                except Exception:
                    pass
                await asyncio.sleep(RECONNECT_INTERVAL)
                continue

            # TODO: intent and shard
            # TODO: resume
            payload = Identify(
                data={
                    "token": self.get_authorization(bot_info),
                    "intents": 513,
                    "shard": [0, 1],
                    "properties": {"$os": sys.platform, "$sdk": "NoneBot2"},
                },
            )

            try:
                payload = await self.receive_payload(ws)
                assert isinstance(payload, Dispatch)
                session_id = payload.data["session_id"]
                user_info = payload.data["user"]
            except Exception as e:
                log(
                    "ERROR",
                    "<r><bg #f8bbd0>Error while receiving server ready event</bg #f8bbd0></r>",
                    e,
                )
                try:
                    await ws.close()
                except Exception:
                    pass
                await asyncio.sleep(RECONNECT_INTERVAL)
                continue

            self.bot_connect(bot)
            try:
                while True:
                    try:
                        payload = await self.receive_payload(ws)
                        event = self.payload_to_event(payload)
                        asyncio.create_task(bot.handle_event(event))
                    except Exception as e:
                        log(
                            "ERROR",
                            "<r><bg #f8bbd0>Error while process data from websocket"
                            f"{escape_tag(str(ws_url))}. Trying to reconnect...</bg #f8bbd0></r>",
                            e,
                        )
                        break
            finally:
                try:
                    await ws.close()
                except Exception:
                    pass
                self.bot_disconnect(bot)

            await asyncio.sleep(RECONNECT_INTERVAL)

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
        ...

    async def _get_guild(self, bot: Bot, guild_id: str) -> Guild:
        request = Request(
            "GET",
            self.get_api_base() / f"guilds/{guild_id}",
        )
        data = await self.request(request)
        assert data.content is not None
        return Guild.parse_raw(data.content)

    async def _get_guild_roles(self, bot: Bot, guild_id: str) -> GuildRoles:
        request = Request(
            "GET",
            self.get_api_base() / f"guilds/{guild_id}/roles",
        )
        data = await self.request(request)
        assert data.content is not None
        return GuildRoles.parse_raw(data.content)

    api_handlers = {
        # Guild API
        "get_guild": _get_guild,
        # Guild Role API
        "get_guild_roles": _get_guild_roles,
    }
