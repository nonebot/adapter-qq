from enum import IntEnum
from datetime import datetime
from typing import List, Union, Optional

from pydantic import (
    Extra,
    Field,
    AnyUrl,
    BaseModel,
    create_model,
    root_validator,
)

from .transformer import BoolToIntTransformer, ExcludeNoneTransformer


class Model(BaseModel, extra=Extra.allow):
    ...


# Guild API
class Guild(BoolToIntTransformer, Model):
    id: str
    name: str
    icon: Optional[str] = None
    owner_id: str
    owner: bool
    memeber_count: int
    max_members: int
    description: str
    joined_at: Optional[datetime] = None


# Guild Role API
class Role(BoolToIntTransformer, Model):
    id: str
    name: str
    color: int
    hoist: bool
    number: int
    memeber_limit: int


class GuildRoles(Model):
    guild_id: str
    roles: List[Role]
    role_num_limit: str


class RoleUpdateFilter(BoolToIntTransformer, Model):
    name: bool
    color: bool
    hoist: bool


class RoleUpdateInfo(BoolToIntTransformer, ExcludeNoneTransformer, Model):
    name: Optional[str] = None
    color: Optional[int] = None
    hoist: Optional[bool] = None

    @root_validator
    def check_field(cls, values):
        if any(map(lambda v: v is not None, values)):
            return values
        raise ValueError("At least one field must be specified.")


class CreateRole(Model):
    role_id: str
    role: Role


class PatchRole(Model):
    guild_id: str
    role_id: str
    role: Role


# Member API
class Member(Model):
    user: "User"
    nick: str
    roles: List[str]
    joined_at: datetime


# Announce API

# Channel API
class ChannelType(IntEnum):
    TEXT = 0
    # Unknown = 1
    AUDIO = 2
    # Unknown = 3
    CHANNEL_GROUP = 4
    LIVE = 10005
    APP = 10006
    FORUM = 10007


class ChannelSubType(IntEnum):
    CHAT = 0
    ANNOUNCE = 1
    STRATEGY = 2
    GAME = 3


class PrivateType(IntEnum):
    PUBLIC = 0
    ADMIN = 1
    SPECIFIED = 2


class Channel(Model):
    id: str
    guild_id: str
    name: str
    type: Union[ChannelType, int]
    sub_type: Union[ChannelSubType, int]
    position: Optional[int] = None
    parent_id: Optional[str] = None
    owner_id: str
    private_type: Optional[PrivateType] = None


# Channel Permissions API

# Message API
class MessageEmbedThumbnail(Model):
    url: AnyUrl


class MessageEmbedField(Model):
    name: str


class MessageEmbed(Model):
    title: str
    prompt: str
    thumbnail: MessageEmbedThumbnail
    fields: List[MessageEmbedField]


class MessageAttachment(Model):
    url: AnyUrl


class MessageArkObjKv(Model):
    key: str
    value: str


class MessageArkObj(Model):
    obj_kv: List[MessageArkObjKv]


class MessageArkKv(Model):
    key: str
    value: str
    obj: List[MessageArkObj]


class MessageArk(Model):
    template_id: int
    kv: List[MessageArkKv]


class MessageMember(Model):
    roles: List[str]
    joined_at: datetime


class Message(Model):
    id: str
    channel_id: str
    guild_id: str
    content: str
    timestamp: datetime
    edited_timestamp: Optional[datetime] = None
    mention_everyone: bool = False
    author: "User"
    attachments: List[MessageAttachment] = Field(default_factory=list)
    embeds: List[MessageEmbed] = Field(default_factory=list)
    mentions: List["User"]
    member: MessageMember
    ark: Optional[MessageArk] = None


# Audio API

# User API
class User(Model):
    id: str
    username: str
    avatar: Optional[str] = None
    bot: bool
    union_openid: Optional[str] = None
    union_user_account: Optional[str] = None


# Schedule API

# Mute API

# WebSocket API
class SessionStartLimit(Model):
    total: int
    remaining: int
    reset_after: int
    max_concurrency: int


class Gateway(Model):
    url: str


class GatewayWithShards(Gateway):
    shards: int
    session_start_limit: SessionStartLimit


Member.update_forward_refs()
Message.update_forward_refs()


__all__ = [
    "Model",
    "Guild",
    "Role",
    "GuildRoles",
    "RoleUpdateFilter",
    "RoleUpdateInfo",
    "CreateRole",
    "PatchRole",
    "Member",
    "ChannelType",
    "ChannelSubType",
    "PrivateType",
    "Channel",
    "MessageEmbedThumbnail",
    "MessageEmbedField",
    "MessageEmbed",
    "MessageAttachment",
    "MessageArkObjKv",
    "MessageArkObj",
    "MessageArkKv",
    "MessageArk",
    "MessageMember",
    "Message",
    "User",
    "SessionStartLimit",
    "Gateway",
    "GatewayWithShards",
]
