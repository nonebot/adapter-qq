from enum import IntEnum
from datetime import datetime
from typing import List, Union, Generic, TypeVar, Optional

from pydantic.generics import GenericModel
from pydantic import BaseModel, validator, root_validator

T = TypeVar("T")


# Guild
class Guild(BaseModel):
    id: int
    name: str
    icon: str
    owner_id: int
    owner: bool
    member_count: int
    max_members: int
    description: str
    joined_at: datetime


# User
class User(BaseModel):
    id: int
    username: str
    avatar: str
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
    id: int
    guild_id: int
    name: str
    type: Union[ChannelType, int]
    sub_type: Union[ChannelSubType, int]
    position: int
    parent_id: Optional[str] = None
    owner_id: Optional[int] = None
    private_type: Union[PrivateType, int]
    speak_permission: Union[SpeakPermission, int]
    application_id: Optional[int] = None
    permissions: Optional[str] = None


# Member
class Member(BaseModel):
    user: Optional[User] = None
    nick: Optional[str] = None
    roles: List[int]
    joined_at: datetime


class GetRoleMembersReturn(BaseModel):
    data: List[Member]
    next: str


# Role
class Role(BaseModel):
    id: int
    name: str
    color: int
    hoist: bool
    number: int
    member_limit: int


class GetGuildRolesReturn(BaseModel):
    guild_id: int
    roles: List[Role]
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
    channel_id: int
    user_id: Optional[int] = None
    role_id: Optional[int] = None
    permissions: int


# Message
# Message Attachment
class MessageAttachment(BaseModel):
    url: str


# Message Embed
class MessageEmbedThumbnail(BaseModel):
    url: str


class MessageEmbedField(BaseModel):
    name: Optional[str] = None


class MessageEmbed(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    prompt: str
    thumbnail: Optional[MessageEmbedThumbnail] = None
    fields: Optional[List[MessageEmbedField]] = None


# Message Ark
class MessageArkObjKv(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None


class MessageArkObj(BaseModel):
    obj_kv: Optional[List[MessageArkObjKv]] = None


class MessageArkKv(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None
    obj: Optional[List[MessageArkObj]] = None


class MessageArk(BaseModel):
    template_id: Optional[int] = None
    kv: Optional[List[MessageArkKv]] = None


# Message Reference
class MessageReference(BaseModel):
    message_id: str
    ignore_get_message_error: Optional[bool] = None


class Message(BaseModel):
    id: str
    channel_id: int
    guild_id: int
    content: Optional[str] = None
    timestamp: datetime
    edited_timestamp: Optional[datetime] = None
    mention_everyone: Optional[bool] = None
    author: User
    attachments: Optional[List[MessageAttachment]] = None
    embeds: Optional[List[MessageEmbed]] = None
    mentions: Optional[List[User]] = None
    member: Member
    ark: Optional[MessageArk] = None
    seq: Optional[int] = None
    seq_in_channel: Optional[str] = None
    message_reference: Optional[MessageReference] = None
    src_guild_id: Optional[int] = None


# Message Markdown
class MessageMarkdownParams(BaseModel):
    key: Optional[str] = None
    values: Optional[List[str]] = None


class MessageMarkdown(BaseModel):
    template_id: Optional[int] = None
    custom_template_id: Optional[str] = None
    params: Optional[MessageMarkdownParams] = None
    content: Optional[str] = None


# Message Keyboard
class Permission(BaseModel):
    type: Optional[int] = None
    specify_role_ids: Optional[List[str]] = None
    specify_user_ids: Optional[List[str]] = None


class Action(BaseModel):
    type: Optional[int] = None
    permission: Optional[Permission] = None
    click_limit: Optional[int] = None
    data: Optional[str] = None
    at_bot_show_channel_list: Optional[bool] = None


class RenderData(BaseModel):
    label: Optional[str] = None
    visited_label: Optional[str] = None
    style: Optional[int] = None


class Button(BaseModel):
    id: Optional[str] = None
    render_data: Optional[RenderData] = None
    action: Optional[Action] = None


class InlineKeyboardRow(BaseModel):
    buttons: Optional[List[Button]] = None


class InlineKeyboard(BaseModel):
    rows: Optional[InlineKeyboardRow] = None


class MessageKeyboard(BaseModel):
    id: Optional[str] = None
    content: Optional[InlineKeyboard] = None


# Message Delete Event
class MessageDelete(BaseModel):
    message: Message
    op_user: User


# Message Audit Event
class MessageAudited(BaseModel):
    audit_id: str
    message_id: Optional[str] = None
    guild_id: str
    channel_id: str
    audit_time: datetime
    create_time: Optional[datetime] = None
    seq_in_channel: Optional[str] = None


# Message Setting
class MessageSetting(BaseModel):
    disable_create_dm: bool
    disable_push_msg: bool
    channel_ids: List[int]
    channel_push_max_num: int


# DMS
class DMS(BaseModel):
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    create_time: Optional[datetime] = None


# Announce
class RecommendChannel(BaseModel):
    channel_id: Optional[int] = None
    introduce: Optional[str] = None


class Announces(BaseModel):
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    message_id: Optional[str] = None
    announces_type: Optional[int] = None
    recommend_channels: Optional[List[RecommendChannel]] = None


# Pins
class PinsMessage(BaseModel):
    guild_id: int
    channel_id: int
    message_ids: List[str]


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
    jump_channel_id: Optional[int] = None
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
    type: Union[ReactionTargetType, int]


class MessageReaction(BaseModel):
    user_id: int
    guild_id: int
    channel_id: int
    target: ReactionTarget
    emoji: Emoji


class GetReactionUsersReturn(BaseModel):
    users: List[User]
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
    guild_id: int
    channel_id: int
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


class ImageElem(BaseModel):
    third_url: str
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

    @root_validator(pre=True, allow_reuse=True)
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
    elems: List[Elem]
    props: Optional[ParagraphProps] = None


class RichText(BaseModel):
    paragraphs: List[Paragraph]


class ThreadObjectInfo(BaseModel):
    thread_id: str
    content: RichText
    date_time: datetime

    @validator("content", pre=True, allow_reuse=True)
    def parse_content(cls, v):
        if isinstance(v, str):
            return RichText.parse_raw(v, content_type="json")
        return v


_T_Title = TypeVar("_T_Title", str, RichText)


class ThreadInfo(ThreadObjectInfo, GenericModel, Generic[_T_Title]):
    # 事件推送拿到的title实际上是RichText的JSON字符串，而API调用返回的title是普通文本
    title: _T_Title

    @validator("title", pre=True, allow_reuse=True)
    def parse_title(cls, v):
        if isinstance(v, str) and cls.__fields__["title"].type_ is RichText:
            return RichText.parse_raw(v, content_type="json")
        return v


class ThreadSourceInfo(BaseModel):
    guild_id: int
    channel_id: int
    author_id: int


class Thread(ThreadSourceInfo, GenericModel, Generic[_T_Title]):
    thread_info: ThreadInfo[_T_Title]


class PostInfo(ThreadObjectInfo):
    post_id: str


class Post(ThreadSourceInfo):
    post_info: PostInfo


class ReplyInfo(ThreadObjectInfo):
    post_id: str
    reply_id: str


class Reply(ThreadSourceInfo):
    reply_info: ReplyInfo


class ForumAuditType(IntEnum):
    THREAD = 1
    POST = 2
    REPLY = 3


class ForumAuditResult(ThreadSourceInfo):
    thread_id: str
    post_id: str
    reply_id: str
    type: ForumAuditType
    result: Optional[int] = None
    err_msg: Optional[str] = None


class GetThreadsListReturn(BaseModel):
    threads: List[Thread[str]]
    is_finish: bool


class GetThreadReturn(BaseModel):
    thread: Thread[str]


class PutThreadReturn(BaseModel):
    task_id: int
    create_time: datetime


# API Permission
class APIPermission(BaseModel):
    path: str
    method: str
    desc: Optional[str] = None
    auth_status: bool


class APIPermissionDemandIdentify(BaseModel):
    path: Optional[str] = None
    name: Optional[str] = None


class APIPermissionDemand(BaseModel):
    guild_id: int
    channel_id: int
    api_identify: APIPermissionDemandIdentify
    title: str
    desc: str


class GetGuildAPIPermissionReturn(BaseModel):
    apis: List[APIPermission]


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
    "Guild",
    "User",
    "ChannelType",
    "ChannelSubType",
    "PrivateType",
    "SpeakPermission",
    "Channel",
    "Member",
    "GetRoleMembersReturn",
    "Role",
    "GetGuildRolesReturn",
    "PostGuildRoleReturn",
    "PatchGuildRoleReturn",
    "ChannelPermissions",
    "MessageAttachment",
    "MessageEmbedThumbnail",
    "MessageEmbedField",
    "MessageEmbed",
    "MessageArkObjKv",
    "MessageArkObj",
    "MessageArkKv",
    "MessageArk",
    "MessageReference",
    "Message",
    "MessageMarkdownParams",
    "MessageMarkdown",
    "Permission",
    "Action",
    "RenderData",
    "Button",
    "InlineKeyboardRow",
    "InlineKeyboard",
    "MessageKeyboard",
    "MessageDelete",
    "MessageAudited",
    "MessageSetting",
    "DMS",
    "RecommendChannel",
    "Announces",
    "PinsMessage",
    "RemindType",
    "Schedule",
    "EmojiType",
    "Emoji",
    "ReactionTargetType",
    "ReactionTarget",
    "MessageReaction",
    "GetReactionUsersReturn",
    "AudioStatus",
    "AudioControl",
    "AudioAction",
    "ElemType",
    "TextProps",
    "TextElem",
    "ImageElem",
    "VideoElem",
    "URLElem",
    "Elem",
    "Alignment",
    "ParagraphProps",
    "Paragraph",
    "RichText",
    "ThreadObjectInfo",
    "ThreadInfo",
    "ThreadSourceInfo",
    "Thread",
    "PostInfo",
    "Post",
    "ReplyInfo",
    "Reply",
    "ForumAuditType",
    "ForumAuditResult",
    "GetThreadsListReturn",
    "GetThreadReturn",
    "PutThreadReturn",
    "APIPermission",
    "APIPermissionDemandIdentify",
    "APIPermissionDemand",
    "GetGuildAPIPermissionReturn",
    "UrlGetReturn",
    "SessionStartLimit",
    "ShardUrlGetReturn",
]
