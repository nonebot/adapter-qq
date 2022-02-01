from typing import TYPE_CHECKING, Any, List, Union, Optional

from nonebot.typing import overrides

from nonebot.adapters import Bot as BaseBot

from .event import Event
from .config import BotInfo
from .message import Message, MessageSegment
from .model import (
    User,
    Guild,
    Member,
    Channel,
    Gateway,
    CreateRole,
    GuildRoles,
    UpdateRole,
    ChannelType,
    PrivateType,
    ChannelSubType,
    SpeakPermission,
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
    def clear(self) -> None: ...
    # User API
    async def get_me(self) -> User: ...
    async def get_me_guilds(
        self,
        *,
        before: str = ...,
        after: str = ...,
        limit: int = ...,
    ) -> List[Guild]: ...
    # Guild API
    async def get_guild(self, *, guild_id: str) -> Guild: ...
    # Channel API
    async def get_channels(self, *, guild_id: str) -> List[Channel]: ...
    async def get_channel(self, *, channel_id: str) -> Channel: ...
    async def create_channel(
        self,
        *,
        guild_id: str,
        name: str,
        type: Union[ChannelType, int] = ...,
        sub_type: Union[ChannelSubType, int] = ...,
        position: int = ...,
        parent_id: str = ...,
        private_type: Union[PrivateType, int] = ...,
        private_user_ids: List[str] = ...,
        speak_permission: Union[SpeakPermission, int] = ...,
        application_id: str = ...,
    ) -> Channel: ...
    async def update_channel(
        self,
        *,
        channel_id: str,
        name: str = ...,
        type: Union[ChannelType, int] = ...,
        position: int = ...,
        parent_id: str = ...,
        private_type: Union[PrivateType, int] = ...,
        speak_permission: Union[SpeakPermission, int] = ...,
    ) -> Channel: ...
    async def delete_channel(self, *, channel_id: str) -> None: ...
    # Member API
    async def get_guild_members(
        self, *, guild_id: str, after: str = ..., limit: int = ...
    ) -> List[Member]: ...
    async def get_guild_member(self, *, guild_id: str, user_id: str) -> Member: ...
    async def delete_guild_member(
        self, *, guild_id: str, user_id: str, add_blacklist: bool = ...
    ) -> None: ...
    # Guild Role API
    async def get_guild_roles(self, *, guild_id: str) -> GuildRoles: ...
    async def create_guild_role(
        self,
        *,
        guild_id: str,
        name: str = ...,
        color: int = ...,
        hoist: int = ...,
    ) -> CreateRole: ...
    async def update_guild_role(
        self,
        *,
        guild_id: str,
        role_id: str,
        name: str = ...,
        color: int = ...,
        hoist: int = ...,
    ) -> UpdateRole: ...
    async def delete_guild_role(self, *, guild_id: str, role_id: str) -> None: ...
    async def create_guild_role_member(
        self,
        *,
        guild_id: str,
        user_id: str,
        role_id: str,
        channel_id: Optional[str] = ...,
    ) -> None: ...
    async def delete_guild_role_member(
        self,
        *,
        guild_id: str,
        user_id: str,
        role_id: str,
        channel_id: Optional[str] = ...,
    ) -> None: ...
    # Channel Permission API
    # Announce API
    # Message API
    # Audio API
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
