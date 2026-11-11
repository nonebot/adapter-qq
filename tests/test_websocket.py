import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing_extensions import override

from nonebot.compat import type_validate_python
from nonebot.drivers import URL, Request, Timeout, WebSocket
import pytest

from nonebot.adapters.qq import Adapter
from nonebot.adapters.qq.bot import Bot
from nonebot.adapters.qq.config import BotInfo


class BlockingWebSocket(WebSocket):
    @property
    @override
    def closed(self) -> bool:
        return False

    @override
    async def accept(self) -> None:
        raise AssertionError

    @override
    async def close(self, code: int = 1000, reason: str = "") -> None:
        raise AssertionError

    @override
    async def receive(self) -> str | bytes:
        await asyncio.Future()
        raise AssertionError

    @override
    async def receive_text(self) -> str:
        raise AssertionError

    @override
    async def receive_bytes(self) -> bytes:
        raise AssertionError

    @override
    async def send_text(self, data: str) -> None:
        raise AssertionError

    @override
    async def send_bytes(self, data: bytes) -> None:
        raise AssertionError


class RequestCapturingAdapter(Adapter):
    def __init__(self, request_received: asyncio.Future[Request]):
        self.request_received = request_received
        self.bots = {}

    @override
    @asynccontextmanager
    async def websocket(self, setup: Request) -> AsyncGenerator[WebSocket, None]:
        self.request_received.set_result(setup)
        yield BlockingWebSocket(request=setup)


@pytest.mark.asyncio
async def test_gateway_request_disables_receive_timeout():
    request_received = asyncio.get_running_loop().create_future()
    adapter = RequestCapturingAdapter(request_received)
    bot_info = type_validate_python(BotInfo, {"id": "BOT", "secret": "SECRET"})
    bot = Bot(adapter, "BOT", bot_info)
    task = asyncio.create_task(
        adapter._forward_ws(
            bot,
            URL("wss://api.bot.qq.com/websocket"),
            (0, 1),
        )
    )

    try:
        request = await asyncio.wait_for(request_received, timeout=1)
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    assert request.timeout == Timeout(
        connect=30.0,
        read=None,
        close=30.0,
    )
