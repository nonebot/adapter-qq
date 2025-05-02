from datetime import datetime
from enum import IntEnum
import json
from typing import Generic, Optional, TypeVar, Union

from pydantic import BaseModel

from nonebot.adapters.qq.compat import field_validator, model_validator
from nonebot.compat import PYDANTIC_V2, model_fields, type_validate_python

from .common import MessageArk, MessageAttachment, MessageEmbed, MessageReference

if PYDANTIC_V2:
    GenericModel = BaseModel
else:
    from pydantic.generics import GenericModel

T = TypeVar("T")


# Guild
class Guild(BaseModel):
    id: str
    name: str
    icon: str
    owner_id: str
    owner: bool
    member_count: int
    max_members: int
    description: str
    joined_at: datetime


# User
class User(BaseModel):
    id: str
    username: Optional[str] = None
    avatar: Optional[str] = None
    bot: Optional[bool] = None
    union_openid: Optional[str] = None
    union_user_account: Optional[str] = None


# Channel
class ChannelType(IntEnum):
    TEXT = 0  # 文字子频道
    # x = 1    # 保留，不可用
    VOICE = 2  # 语音子频道
    # x = 3    # 保留，不可用
    GROUP = 4  # 子频道分组
    LIVE = 10005  # 直播子频道
    APP = 10006  # 应用子频道
    DISCUSSION = 10007  # 论坛子频道


class ChannelSubType(IntEnum):
    TALK = 0  # 闲聊
    POST = 1  # 公告
    CHEAT = 2  # 攻略
    BLACK = 3  # 开黑


class PrivateType(IntEnum):
    PUBLIC = 0  # 公开频道
    ADMIN = 1  # 管理员和群主可见
    SPECIFIED_USER = 2  # 群主管理员+指定成员，可使用 修改子频道权限接口 指定成员


class SpeakPermission(IntEnum):
    INVALID = 0  # 无效类型
    EVERYONE = 1  # 所有人
    ADMIN = 2  # 群主管理员+指定成员，可使用 修改子频道权限接口 指定成员


class Channel(BaseModel):
    id: str
    guild_id: str
    name: str
    type: Union[ChannelType, int]
    sub_type: Union[ChannelSubType, int]
    position: int
    parent_id: Optional[str] = None
    owner_id: Optional[str] = None
    private_type: Optional[Union[PrivateType, int]] = None
    speak_permission: Optional[Union[SpeakPermission, int]] = None
    application_id: Optional[str] = None
    permissions: Optional[int] = None


# Member
class Member(BaseModel):
    user: Optional[User] = None
    nick: Optional[str] = None
    roles: Optional[list[str]] = None
    joined_at: datetime


class GetRoleMembersReturn(BaseModel):
    data: list[Member]
    next: str


# Role
class Role(BaseModel):
    id: str
    name: str
    color: int
    hoist: bool
    number: int
    member_limit: int


class GetGuildRolesReturn(BaseModel):
    guild_id: str
    roles: list[Role]
    role_num_limit: int


class PostGuildRoleReturn(BaseModel):
    role_id: str
    role: Role


class PatchGuildRoleReturn(BaseModel):
    guild_id: str
    role_id: str
    role: Role


# Channel Permission
class ChannelPermissions(BaseModel):
    channel_id: str
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    permissions: int


# Message
class Message(BaseModel):
    id: str
    channel_id: str
    guild_id: str
    content: Optional[str] = None
    timestamp: Optional[datetime] = None
    edited_timestamp: Optional[datetime] = None
    mention_everyone: Optional[bool] = None
    author: User
    attachments: Optional[list[MessageAttachment]] = None
    embeds: Optional[list[MessageEmbed]] = None
    mentions: Optional[list[User]] = None
    member: Optional[Member] = None
    ark: Optional[MessageArk] = None
    seq: Optional[int] = None
    seq_in_channel: Optional[str] = None
    message_reference: Optional[MessageReference] = None
    src_guild_id: Optional[str] = None


# Message Delete Event
class MessageDelete(BaseModel):
    message: Message
    op_user: User


# Message Setting
class MessageSetting(BaseModel):
    disable_create_dm: bool
    disable_push_msg: bool
    channel_ids: list[str]
    channel_push_max_num: int


# DMS
class DMS(BaseModel):
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    create_time: Optional[datetime] = None


# Announce
class RecommendChannel(BaseModel):
    channel_id: Optional[str] = None
    introduce: Optional[str] = None


class Announces(BaseModel):
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    message_id: Optional[str] = None
    announces_type: Optional[int] = None
    recommend_channels: Optional[list[RecommendChannel]] = None


# Pins
class PinsMessage(BaseModel):
    guild_id: str
    channel_id: str
    message_ids: list[str]


# Schedule
class RemindType(IntEnum):
    NO_REMIND = 0
    REMIND_START = 1
    REMIND_5_MIN = 2
    REMIND_15_MIN = 3
    REMIND_30_MIN = 4
    REMIND_60_MIN = 5


class Schedule(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    start_timestamp: datetime
    end_timestamp: datetime
    creator: Optional[Member] = None
    jump_channel_id: Optional[str] = None
    remind_type: Optional[Union[RemindType, int]] = None


# Emoji Reaction
class EmojiType(IntEnum):
    SYSTEM = 1
    CUSTOM = 2


class Emoji(BaseModel):
    id: str
    type: int


class ReactionTargetType(IntEnum):
    MESSAGE = 0
    FEED = 1
    COMMENT = 2
    REPLY = 3


class ReactionTarget(BaseModel):
    id: str
    type: Union[ReactionTargetType, str]


class MessageReaction(BaseModel):
    user_id: str
    guild_id: str
    channel_id: str
    target: ReactionTarget
    emoji: Emoji


class GetReactionUsersReturn(BaseModel):
    users: list[User]
    cookie: str
    is_end: bool


# Audio
class AudioStatus(IntEnum):
    START = 0
    PAUSE = 1
    RESUME = 2
    STOP = 3


class AudioControl(BaseModel):
    audio_url: Optional[str] = None
    text: Optional[str] = None
    status: Union[AudioStatus, int]


class AudioAction(BaseModel):
    guild_id: str
    channel_id: str
    audio_url: Optional[str] = None
    text: Optional[str] = None


# Forum
class ElemType(IntEnum):
    UNSUPPORTED = 0
    TEXT = 1
    IMAGE = 2
    VIDEO = 3
    URL = 4


class TextProps(BaseModel):
    font_bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None


class TextElem(BaseModel):
    text: str
    props: Optional[TextProps] = None


class PlatImage(BaseModel):
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    image_id: Optional[str] = None


class ImageElem(BaseModel):
    plat_image: Optional[PlatImage] = None
    third_url: Optional[str] = None
    width_percent: Optional[float] = None


class VideoElem(BaseModel):
    third_url: str


class URLElem(BaseModel):
    url: str
    desc: Optional[str] = None


class Elem(BaseModel):
    type: ElemType
    text: Optional[TextElem] = None
    image: Optional[ImageElem] = None
    video: Optional[VideoElem] = None
    url: Optional[URLElem] = None

    @model_validator(mode="before")
    @classmethod
    def infer_type(cls, values: dict):
        if values.get("type") is not None:
            return values

        if values.get("text") is not None:
            values["type"] = ElemType.TEXT
        elif values.get("image") is not None:
            values["type"] = ElemType.IMAGE
        elif values.get("video") is not None:
            values["type"] = ElemType.VIDEO
        elif values.get("url") is not None:
            values["type"] = ElemType.URL
        else:
            # Unsupported element type
            values["type"] = ElemType.UNSUPPORTED

        return values


class Alignment(IntEnum):
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2


class ParagraphProps(BaseModel):
    alignment: Optional[Alignment] = None


class Paragraph(BaseModel):
    elems: list[Elem]
    props: Optional[ParagraphProps] = None


class RichText(BaseModel):
    paragraphs: Optional[list[Paragraph]] = None


class ThreadObjectInfo(BaseModel):
    thread_id: str
    content: RichText
    date_time: datetime

    @field_validator("content", mode="before")
    @classmethod
    def parse_content(cls, v):
        if isinstance(v, str):
            return type_validate_python(RichText, json.loads(v))
        return v


_T_Title = TypeVar("_T_Title", str, RichText)


class ThreadInfo(ThreadObjectInfo, GenericModel, Generic[_T_Title]):
    # 事件推送拿到的title实际上是RichText的JSON字符串，而API调用返回的title是普通文本
    title: _T_Title

    @field_validator("title", mode="before")
    @classmethod
    def parse_title(cls, v):
        if (
            isinstance(v, str)
            and next(f for f in model_fields(cls) if f.name == "title").annotation
            is RichText
        ):
            return type_validate_python(RichText, json.loads(v))
        return v


class ForumSourceInfo(BaseModel):
    guild_id: str
    channel_id: str
    author_id: str


class Thread(ForumSourceInfo, GenericModel, Generic[_T_Title]):
    thread_info: ThreadInfo[_T_Title]


class PostInfo(ThreadObjectInfo):
    post_id: str


class Post(ForumSourceInfo):
    post_info: PostInfo


class ReplyInfo(ThreadObjectInfo):
    post_id: str
    reply_id: str


class Reply(ForumSourceInfo):
    reply_info: ReplyInfo


class ForumAuditType(IntEnum):
    THREAD = 1
    POST = 2
    REPLY = 3


class ForumAuditResult(ForumSourceInfo):
    thread_id: str
    post_id: str
    reply_id: str
    type: ForumAuditType
    result: Optional[int] = None
    err_msg: Optional[str] = None


class GetThreadsListReturn(BaseModel):
    threads: list[Thread[str]]
    is_finish: bool


class GetThreadReturn(BaseModel):
    thread: Thread[str]


class PutThreadReturn(BaseModel):
    task_id: str
    create_time: datetime


# API Permission
class APIPermission(BaseModel):
    path: str
    method: str
    desc: Optional[str] = None
    auth_status: bool


class APIPermissionDemandIdentify(BaseModel):
    path: Optional[str] = None
    method: Optional[str] = None


class APIPermissionDemand(BaseModel):
    guild_id: str
    channel_id: str
    api_identify: APIPermissionDemandIdentify
    title: str
    desc: str


class GetGuildAPIPermissionReturn(BaseModel):
    apis: list[APIPermission]


# WebSocket
class UrlGetReturn(BaseModel):
    url: str


class SessionStartLimit(BaseModel):
    total: int
    remaining: int
    reset_after: int
    max_concurrency: int


class ShardUrlGetReturn(BaseModel):
    url: str
    shards: int
    session_start_limit: SessionStartLimit


__all__ = [
    "DMS",
    "APIPermission",
    "APIPermissionDemand",
    "APIPermissionDemandIdentify",
    "Alignment",
    "Announces",
    "AudioAction",
    "AudioControl",
    "AudioStatus",
    "Channel",
    "ChannelPermissions",
    "ChannelSubType",
    "ChannelType",
    "Elem",
    "ElemType",
    "Emoji",
    "EmojiType",
    "ForumAuditResult",
    "ForumAuditType",
    "ForumSourceInfo",
    "GetGuildAPIPermissionReturn",
    "GetGuildRolesReturn",
    "GetReactionUsersReturn",
    "GetRoleMembersReturn",
    "GetThreadReturn",
    "GetThreadsListReturn",
    "Guild",
    "ImageElem",
    "Member",
    "Message",
    "MessageDelete",
    "MessageReaction",
    "MessageSetting",
    "Paragraph",
    "ParagraphProps",
    "PatchGuildRoleReturn",
    "PinsMessage",
    "Post",
    "PostGuildRoleReturn",
    "PostInfo",
    "PrivateType",
    "PutThreadReturn",
    "ReactionTarget",
    "ReactionTargetType",
    "RecommendChannel",
    "RemindType",
    "Reply",
    "ReplyInfo",
    "RichText",
    "Role",
    "Schedule",
    "SessionStartLimit",
    "ShardUrlGetReturn",
    "SpeakPermission",
    "TextElem",
    "TextProps",
    "Thread",
    "ThreadInfo",
    "ThreadObjectInfo",
    "URLElem",
    "UrlGetReturn",
    "User",
    "VideoElem",
]
