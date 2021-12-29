from typing_extensions import Literal
from typing import TYPE_CHECKING, Any, Union, Optional

from nonebot.typing import overrides

from nonebot.adapters import Bot as BaseBot

from .event import Event
from .config import BotInfo
from .message import Message, MessageSegment
from .model import (
    User,
    Guild,
    Member,
    Gateway,
    PatchRole,
    CreateRole,
    GuildRoles,
    GatewayWithShards,
)

if TYPE_CHECKING:
    from .adapter import Adapter

class Bot(BaseBot):
    bot_info: BotInfo
    def __init__(self, adapter: "Adapter", bot_info: BotInfo): ...
    @property
    def ready(self) -> bool: ...
    @property
    def session_id(self) -> str: ...
    @session_id.setter
    def session_id(self, session_id: str) -> None: ...
    @property
    def self_info(self) -> User: ...
    @self_info.setter
    def self_info(self, self_info: User) -> None: ...
    @property
    def has_sequence(self) -> bool: ...
    @property
    def sequence(self) -> int: ...
    @sequence.setter
    def sequence(self, sequence: int) -> None: ...
    # Guild API
    async def get_guild(self, guild_id: str) -> Guild: ...
    # Guild Role API
    async def get_guild_roles(self, guild_id: str) -> GuildRoles: ...
    async def create_guild_role(
        self, guild_id: str, name: str, color: int, hoist: bool
    ) -> CreateRole: ...
    async def patch_guild_role(
        self,
        guild_id: str,
        role_id: str,
        *,
        name: Optional[str] = None,
        color: Optional[int] = None,
        hoist: Optional[bool] = None,
    ) -> PatchRole: ...
    async def delete_guild_role(self, guild_id: str, role_id: str) -> None: ...
    async def put_guild_member_role(
        self,
        guild_id: str,
        user_id: str,
        role_id: str,
        channel_id: Optional[str] = None,
    ) -> None: ...
    async def delete_guild_member_role(
        self,
        guild_id: str,
        user_id: str,
        role_id: str,
        channel_id: Optional[str] = None,
    ) -> None: ...
    # Member API
    async def get_member(self, guild_id: str, user_id: str) -> Member: ...
    # Announce API
    # Channel API
    # Channel Permission API
    # Message API
    # Audio API
    # User API
    # Schedule API
    # Mute API
    # WebSocket API
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
