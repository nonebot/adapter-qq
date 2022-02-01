from enum import IntEnum
from datetime import datetime
from typing import List, Union, Optional
from typing_extensions import Literal, Annotated

from pydantic import Extra, Field, AnyUrl, BaseModel, root_validator

from .transformer import BoolToIntTransformer, ExcludeNoneTransformer


class Model(BaseModel, extra=Extra.allow):
    ...


# User API
class User(Model):
    id: str
    username: str
    # 用户头像可能为空（默认头像）
    avatar: Optional[AnyUrl] = None
    bot: bool
    # 互联应用，申请互联应用后可以获取
    union_openid: Optional[str] = None
    union_user_account: Optional[str] = None


# Guild API
class Guild(BoolToIntTransformer, Model):
    id: str
    name: str
    icon: str
    owner_id: str
    owner: bool
    memeber_count: int
    max_members: int
    description: str
    joined_at: datetime


# Channel API
class ChannelType(IntEnum):
    TEXT = 0
    # Unknown = 1
    VOICE = 2
    # Unknown = 3
    CATEGORY = 4
    LIVE = 10005
    APP = 10006
    FORUM = 10007


class ChannelSubType(IntEnum):
    CHAT = 0
    NOTICE = 1
    GUIDE = 2
    GAME = 3


class PrivateType(IntEnum):
    PUBLIC = 0
    ADMIN = 1
    SPECIFIED = 2


class SpeakPermission(IntEnum):
    PUBLIC = 1
    SPECIFIED = 2


class Channel(Model):
    id: str
    guild_id: str
    name: str
    type: Union[ChannelType, int]
    sub_type: Union[ChannelSubType, int]
    position: int
    parent_id: str
    owner_id: str
    private_type: Optional[PrivateType] = None
    private_user_ids: Optional[List[str]] = None
    speak_permission: Optional[SpeakPermission] = None
    application_id: Optional[str] = None


class TextChannel(Channel):
    type: Literal[ChannelType.TEXT]
    private_type: PrivateType
    speak_permission: SpeakPermission


class VoiceChannel(Channel):
    type: Literal[ChannelType.VOICE]
    private_type: PrivateType
    speak_permission: SpeakPermission


class ChannelCategory(Channel):
    type: Literal[ChannelType.CATEGORY]


class LiveChannel(Channel):
    type: Literal[ChannelType.LIVE]
    private_type: PrivateType
    speak_permission: SpeakPermission


class AppChannel(Channel):
    type: Literal[ChannelType.APP]
    private_type: PrivateType
    speak_permission: SpeakPermission
    application_id: str


class ForumChannel(Channel):
    type: Literal[ChannelType.FORUM]
    private_type: PrivateType
    speak_permission: SpeakPermission


_ChannelType = Union[
    Annotated[
        Union[
            TextChannel,
            VoiceChannel,
            ChannelCategory,
            LiveChannel,
            AppChannel,
            ForumChannel,
        ],
        Field(discriminator="type"),
    ],
    Channel,
]


# Member API
class Member(Model):
    user: User
    nick: str
    roles: List[str]
    joined_at: datetime


class MemberWithGuildID(Member):
    guild_id: str


# Guild Role API
class Role(BoolToIntTransformer, Model):
    id: str
    name: str
    color: int
    hoist: bool
    number: int
    member_limit: int


class GuildRoles(Model):
    guild_id: str
    roles: List[Role]
    role_num_limit: str


class RoleCreateInfo(BoolToIntTransformer, Model):
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


class UpdateRole(Model):
    guild_id: str
    role_id: str
    role: Role


# Channel Permissions API
class ChannelPermissions(Model):
    channel_id: str
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    permissions: str


class ChannelUserPermissions(ChannelPermissions):
    user_id: str


class ChannelRolePermissions(ChannelPermissions):
    role_id: str


_ChannelPermissionsType = Union[ChannelUserPermissions, ChannelRolePermissions]


# Announce API

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


Message.update_forward_refs()


__all__ = [
    "Model",
    "User",
    "Guild",
    "ChannelType",
    "ChannelSubType",
    "PrivateType",
    "SpeakPermission",
    "Channel",
    "TextChannel",
    "VoiceChannel",
    "ChannelCategory",
    "LiveChannel",
    "AppChannel",
    "ForumChannel",
    "Member",
    "MemberWithGuildID",
    "Role",
    "GuildRoles",
    "RoleCreateInfo",
    "CreateRole",
    "UpdateRole",
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
    "SessionStartLimit",
    "Gateway",
    "GatewayWithShards",
]
