import asyncio
import binascii
import json
import sys
from typing import Any, Literal, Optional, Union, cast
from typing_extensions import override

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from nonebot import get_plugin_config
from nonebot.adapters import Adapter as BaseAdapter
from nonebot.compat import PYDANTIC_V2, type_validate_json, type_validate_python
from nonebot.drivers import (
    URL,
    ASGIMixin,
    Driver,
    HTTPClientMixin,
    HTTPServerSetup,
    Request,
    Response,
    WebSocket,
    WebSocketClientMixin,
)
from nonebot.exception import WebSocketClosed
from nonebot.utils import escape_tag

from .bot import Bot
from .config import BotInfo, Config
from .event import EVENT_CLASSES, Event, MessageAuditEvent, ReadyEvent
from .exception import ApiNotAvailable
from .models import (
    Dispatch,
    Heartbeat,
    HeartbeatAck,
    Hello,
    Identify,
    InvalidSession,
    Payload,
    PayloadType,
    Reconnect,
    Resume,
    WebhookVerify,
)
from .store import audit_result
from .utils import API, log

RECONNECT_INTERVAL = 3.0


class Adapter(BaseAdapter):
    @override
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)

        self.qq_config: Config = get_plugin_config(Config)

        self.tasks: set["asyncio.Task"] = set()
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

        if any(bot.use_websocket for bot in self.qq_config.qq_bots) and not isinstance(
            self.driver, WebSocketClientMixin
        ):
            raise RuntimeError(
                f"Current driver {self.config.driver} does not support "
                "websocket client! "
                "QQ Adapter need a WebSocketClient Driver to work."
            )

        if not all(
            bot.use_websocket for bot in self.qq_config.qq_bots
        ) and not isinstance(self.driver, ASGIMixin):
            raise RuntimeError(
                f"Current driver {self.config.driver} does not support "
                "ASGI server! "
                "QQ Adapter need a ASGI Driver to receive webhook."
            )
        self.on_ready(self.startup)
        self.driver.on_shutdown(self.shutdown)

    async def startup(self) -> None:
        log("DEBUG", f"QQ run in sandbox mode: <y>{self.qq_config.qq_is_sandbox}</y>")

        try:
            api_base = self.get_api_base()
        except Exception as e:
            log("ERROR", "Failed to parse QQ api base url", e)
            raise

        log("DEBUG", f"QQ api base url: <y>{escape_tag(str(api_base))}</y>")

        if isinstance(self.driver, ASGIMixin):
            self.setup_http_server(
                HTTPServerSetup(
                    URL("/qq/"),
                    "POST",
                    f"{self.get_name()} Root Webhook",
                    self._handle_http,
                ),
            )
            self.setup_http_server(
                HTTPServerSetup(
                    URL("/qq/webhook"),
                    "POST",
                    f"{self.get_name()} Webhook",
                    self._handle_http,
                ),
            )
            self.setup_http_server(
                HTTPServerSetup(
                    URL("/qq/webhook/"),
                    "POST",
                    f"{self.get_name()} Webhook Slash",
                    self._handle_http,
                ),
            )

        for bot in self.qq_config.qq_bots:
            if not bot.use_websocket:
                continue
            task = asyncio.create_task(self.run_bot_websocket(bot))
            task.add_done_callback(self.tasks.discard)
            self.tasks.add(task)

    async def shutdown(self) -> None:
        for task in self.tasks:
            if not task.done():
                task.cancel()

        await asyncio.gather(
            *(asyncio.wait_for(task, timeout=10) for task in self.tasks),
            return_exceptions=True,
        )

    async def run_bot_websocket(self, bot_info: BotInfo) -> None:
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
            task = asyncio.create_task(self._forward_ws(bot, ws_url, bot_info.shard))
            task.add_done_callback(self.tasks.discard)
            self.tasks.add(task)
            return

        # start connection in sharding mode
        shards = gateway_info.shards or 1
        for i in range(shards):
            task = asyncio.create_task(self._forward_ws(bot, ws_url, (i, shards)))
            task.add_done_callback(self.tasks.discard)
            self.tasks.add(task)
            # wait for session start concurrency limit
            await asyncio.sleep(gateway_info.session_start_limit.max_concurrency or 1)

    async def _forward_ws(self, bot: Bot, ws_url: URL, shard: tuple[int, int]) -> None:
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
            assert isinstance(payload, Hello), (
                f"Received unexpected payload: {payload!r}"
            )
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
        self, bot: Bot, ws: WebSocket, shard: tuple[int, int]
    ) -> Optional[Literal[True]]:
        """鉴权连接"""
        if not bot.ready:
            payload = type_validate_python(
                Identify,
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
                    }
                },
            )
        else:
            payload = type_validate_python(
                Resume,
                {
                    "data": {
                        "token": await bot._get_authorization_header(),
                        "session_id": bot.session_id,
                        "seq": bot.sequence,
                    }
                },
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
            task = asyncio.create_task(bot.handle_event(ready_event))
            task.add_done_callback(self.tasks.discard)
            self.tasks.add(task)

        return True

    async def _heartbeat(self, bot: Bot, ws: WebSocket, heartbeat_interval: int):
        """心跳"""
        while True:
            if bot.ready:
                log("TRACE", f"Heartbeat {bot.sequence}")
                payload = type_validate_python(Heartbeat, {"data": bot.sequence})
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
                self.dispatch_event(bot, payload)
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

    async def receive_payload(self, bot: Bot, ws: WebSocket) -> Payload:
        return self.data_to_payload(bot, await ws.receive())

    async def _handle_http(self, request: Request) -> Response:
        bot_id = request.headers.get("X-Bot-Appid")
        if not bot_id:
            log("WARNING", "Missing X-Bot-Appid header in request")
            return Response(403, content="Missing X-Bot-Appid header")
        elif bot_id in self.bots:
            bot = cast(Bot, self.bots[bot_id])
        elif bot_info := next(
            (bot_info for bot_info in self.qq_config.qq_bots if bot_info.id == bot_id),
            None,
        ):
            bot = Bot(self, bot_id, bot_info)
        else:
            log("ERROR", f"Bot {bot_id} not found")
            return Response(403, content="Bot not found")

        if request.content is None:
            return Response(400, content="Missing request content")

        try:
            payload = self.data_to_payload(bot, request.content)
        except Exception as e:
            log(
                "ERROR",
                "<r><bg #f8bbd0>Error while parsing data from webhook</bg #f8bbd0></r>",
                e,
            )
            return Response(400, content="Invalid request content")

        log(
            "TRACE",
            f"Received payload: {escape_tag(repr(payload))}",
        )
        if isinstance(payload, WebhookVerify):
            log("INFO", "Received qq webhook verify request")
            return self._webhook_verify(bot, payload)

        if self.qq_config.qq_verify_webhook and (
            response := self._check_signature(bot, request)
        ):
            return response

        # ensure bot self info
        if not bot._self_info:
            bot.self_info = await bot.me()

        if bot.self_id not in self.bots:
            self.bot_connect(bot)

        if isinstance(payload, Dispatch):
            self.dispatch_event(bot, payload)

        return Response(200)

    def _get_ed25519_key(self, bot: Bot) -> Ed25519PrivateKey:
        secret = bot.bot_info.secret.encode()
        seed = secret
        while len(seed) < 32:
            seed += secret
        seed = seed[:32]
        return Ed25519PrivateKey.from_private_bytes(seed)

    def _webhook_verify(self, bot: Bot, payload: WebhookVerify) -> Response:
        plain_token = payload.data.plain_token
        event_ts = payload.data.event_ts

        try:
            private_key = self._get_ed25519_key(bot)
        except Exception as e:
            log("ERROR", "Failed to create private key", e)
            return Response(500, content="Failed to create private key")

        msg = f"{event_ts}{plain_token}".encode()
        try:
            signature = private_key.sign(msg)
            signature_hex = binascii.hexlify(signature).decode()
        except Exception as e:
            log("ERROR", "Failed to sign message", e)
            return Response(500, content="Failed to sign message")

        return Response(
            200,
            content=json.dumps(
                {"plain_token": plain_token, "signature": signature_hex}
            ),
        )

    def _check_signature(self, bot: Bot, request: Request) -> Optional[Response]:
        signature = request.headers.get("X-Signature-Ed25519")
        timestamp = request.headers.get("X-Signature-Timestamp")
        if not signature or not timestamp:
            log("WARNING", "Missing signature or timestamp in request")
            return Response(403, content="Missing signature or timestamp")

        if request.content is None:
            return Response(400, content="Missing request content")

        try:
            private_key = self._get_ed25519_key(bot)
            public_key = private_key.public_key()
        except Exception as e:
            log("ERROR", "Failed to create public key", e)
            return Response(500, content="Failed to create public key")

        signature = binascii.unhexlify(signature)
        if len(signature) != 64 or signature[63] & 224 != 0:
            log("WARNING", "Invalid signature in request")
            return Response(403, content="Invalid signature")

        body = (
            request.content.encode()
            if isinstance(request.content, str)
            else request.content
        )
        msg = timestamp.encode() + body
        try:
            public_key.verify(signature, msg)
        except InvalidSignature:
            log("WARNING", "Invalid signature in request")
            return Response(403, content="Invalid signature")
        except Exception as e:
            log("ERROR", "Failed to verify signature", e)
            return Response(403, content="Failed to verify signature")

    def get_auth_base(self) -> URL:
        return URL(str(self.qq_config.qq_auth_base))

    def get_api_base(self) -> URL:
        if self.qq_config.qq_is_sandbox:
            return URL(str(self.qq_config.qq_sandbox_api_base))
        else:
            return URL(str(self.qq_config.qq_api_base))

    @staticmethod
    def data_to_payload(bot: Bot, data: Union[str, bytes]) -> Payload:
        payload = type_validate_json(PayloadType, data)
        if isinstance(payload, Dispatch):
            bot.on_dispatch(payload)
        return payload

    @staticmethod
    def payload_to_json(payload: Payload) -> str:
        if PYDANTIC_V2:
            return payload.model_dump_json(by_alias=True)

        return payload.json(by_alias=True)

    def dispatch_event(self, bot: Bot, payload: Dispatch):
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
            task = asyncio.create_task(bot.handle_event(event))
            task.add_done_callback(self.tasks.discard)
            self.tasks.add(task)

    @staticmethod
    def payload_to_event(payload: Dispatch) -> Event:
        EventClass = EVENT_CLASSES.get(payload.type, None)
        if EventClass is None:
            log("WARNING", f"Unknown payload type: {payload.type}")
            event = type_validate_python(
                Event, {"event_id": payload.id, **payload.data}
            )
            event.__type__ = payload.type  # type: ignore
            return event
        return type_validate_python(
            EventClass, {"event_id": payload.id, **payload.data}
        )

    @override
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        log("DEBUG", f"Bot {bot.bot_info.id} calling API <y>{api}</y>")
        api_handler: Optional[API] = getattr(bot.__class__, api, None)
        if api_handler is None:
            raise ApiNotAvailable
        return await api_handler(bot, **data)
