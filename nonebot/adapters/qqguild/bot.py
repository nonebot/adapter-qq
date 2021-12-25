from typing import Any, Union

from nonebot.typing import overrides
from nonebot.message import handle_event

from nonebot.adapters import Bot as BaseBot

from .event import Event
from .message import Message, MessageSegment
from .model import Gateway, GatewayWithShards


class Bot(BaseBot):
    async def gateway(self) -> Gateway:
        data = await self.call_api("/gateway")
        return Gateway.parse_obj(data)

    async def gateway_with_shards(self) -> GatewayWithShards:
        data = await self.call_api("/gateway/bot")
        return GatewayWithShards.parse_obj(data)

    async def handle_event(self, event: Event) -> None:
        await handle_event(self, event)

    @overrides(BaseBot)
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs,
    ) -> Any:
        ...
