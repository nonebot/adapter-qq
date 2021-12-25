from typing_extensions import Literal
from typing import Any, Union, Optional

from nonebot.typing import overrides
from nonebot.message import handle_event

from nonebot.adapters import Bot as BaseBot

from .event import Event
from .message import Message, MessageSegment
from .model import (
    Guild,
    Gateway,
    PatchRole,
    CreateRole,
    GuildRoles,
    GatewayWithShards,
)

class Bot(BaseBot):
    # Guild API
    async def get_guild(self, guild_id: str) -> Guild: ...
    async def get_guild_roles(self, guild_id: str) -> GuildRoles: ...
    async def create_guild_role(
        self, guild_id: str, name: str, color: int, hoist: Literal[0, 1]
    ) -> CreateRole: ...
    async def patch_guild_role(
        self,
        guild_id: str,
        role_id: str,
        *,
        name: Optional[str] = None,
        color: Optional[int] = None,
        hoist: Optional[Literal[0, 1]] = None,
    ) -> PatchRole: ...
    async def get_gateway(self) -> Gateway: ...
    async def get_gateway_with_shards(self) -> GatewayWithShards: ...
    async def handle_event(self, event: Event) -> None: ...
    @overrides(BaseBot)
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs,
    ) -> Any: ...
