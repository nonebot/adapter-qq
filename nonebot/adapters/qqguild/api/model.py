import json
from datetime import datetime
from enum import IntEnum
from typing import List, Literal, Optional, Generic, TypeVar

from pydantic import BaseModel, validator
from pydantic.generics import GenericModel


class Guild(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    icon: Optional[str] = None
    owner_id: Optional[int] = None
    owner: Optional[bool] = None
    member_count: Optional[int] = None
    max_members: Optional[int] = None
    description: Optional[str] = None
    joined_at: Optional[str] = None


class User(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    bot: Optional[bool] = None
    union_openid: Optional[str] = None
    union_user_account: Optional[str] = None


class ChannelCreate(BaseModel):
    name: str
    type: int
    sub_type: int
    position: Optional[int] = None
    parent_id: Optional[int] = None
    private_type: Optional[int] = None
    private_user_ids: Optional[List[int]] = None


class Channel(BaseModel):
    id: Optional[int] = None
    guild_id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[int] = None
    sub_type: Optional[int] = None
    position: Optional[int] = None
    parent_id: Optional[str] = None
    owner_id: Optional[int] = None
    private_type: Optional[int] = None
    speak_permission: Optional[int] = None
    application_id: Optional[str] = None


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[int] = None
    sub_type: Optional[int] = None
    position: Optional[int] = None
    parent_id: Optional[int] = None
    private_type: Optional[int] = None


class Member(BaseModel):
    user: Optional[User] = None
    nick: Optional[str] = None
    roles: Optional[List[int]] = None
    joined_at: Optional[datetime] = None


class DeleteMemberBody(BaseModel):
    add_blacklist: Optional[bool] = None
    delete_history_msg_days: Optional[Literal[-1, 0, 3, 7, 15, 30]] = None


class Role(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    color: Optional[int] = None
    hoist: Optional[int] = None
    number: Optional[int] = None
    member_limit: Optional[int] = None


class GetGuildRolesReturn(BaseModel):
    guild_id: Optional[str] = None
    roles: Optional[List[Role]] = None
    role_num_limit: Optional[str] = None


class PostGuildRoleBody(BaseModel):
    name: str
    color: Optional[float] = None
    hoist: Optional[float] = None


class GuildRole(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    color: Optional[float] = None
    hoist: Optional[float] = None
    number: Optional[float] = None
    member_limit: Optional[float] = None


class PostGuildRoleReturn(BaseModel):
    role_id: Optional[str] = None
    role: Optional[GuildRole] = None


class PatchGuildRoleBody(BaseModel):
    name: Optional[str] = None
    color: Optional[float] = None
    hoist: Optional[float] = None


class PatchGuildRoleReturn(BaseModel):
    guild_id: Optional[str] = None
    role_id: Optional[str] = None
    role: Optional[GuildRole] = None


class PutGuildMemberRoleBody(BaseModel):
    id: Optional[str] = None


class DeleteGuildMemberRoleBody(BaseModel):
    id: Optional[str] = None


class ChannelPermissions(BaseModel):
    channel_id: Optional[int] = None
    user_id: Optional[int] = None
    role_id: Optional[int] = None
    permissions: Optional[str] = None


class PutChannelPermissionsBody(BaseModel):
    add: Optional[str] = None
    remove: Optional[str] = None


class PutChannelRolesPermissionsBody(BaseModel):
    add: Optional[str] = None
    remove: Optional[str] = None


class MessageAttachment(BaseModel):
    url: Optional[str] = None


class MessageEmbedThumbnail(BaseModel):
    url: Optional[str] = None


class MessageEmbedField(BaseModel):
    name: Optional[str] = None


class MessageEmbed(BaseModel):
    title: Optional[str] = None
    prompt: Optional[str] = None
    thumbnail: Optional[MessageEmbedThumbnail] = None
    fields: Optional[List[MessageEmbedField]] = None


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


class MessageReference(BaseModel):
    message_id: Optional[str] = None
    ignore_get_message_error: Optional[bool] = None


class MessageMarkdownParams(BaseModel):
    key: Optional[str]
    values: Optional[List[str]]


class MessageMarkdown(BaseModel):
    template_id: Optional[int]
    custom_template_id: Optional[str]
    params: Optional[MessageMarkdownParams]
    content: Optional[str]


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
    render_data: Optional[bool] = None
    action: Optional[bool] = None


class InlineKeyboardRow(BaseModel):
    buttons: Optional[List[Button]] = None


class InlineKeyboard(BaseModel):
    rows: Optional[InlineKeyboardRow] = None


class MessageKeyboard(BaseModel):
    id: Optional[str] = None
    content: Optional[InlineKeyboard] = None


class Message(BaseModel):
    id: Optional[str] = None
    channel_id: Optional[int] = None
    guild_id: Optional[int] = None
    content: Optional[str] = None
    timestamp: Optional[datetime] = None
    edited_timestamp: Optional[datetime] = None
    mention_everyone: Optional[bool] = None
    author: Optional[User] = None
    attachments: Optional[List[MessageAttachment]] = None
    embeds: Optional[List[MessageEmbed]] = None
    mentions: Optional[List[User]] = None
    member: Optional[Member] = None
    ark: Optional[MessageArk] = None
    seq: Optional[int] = None
    seq_in_channel: Optional[str] = None
    message_reference: Optional[MessageReference] = None
    src_guild_id: Optional[str] = None


class MessageGet(BaseModel):
    message: Optional[Message] = None


class MessageDelete(BaseModel):
    message: Optional[Message] = None
    op_user: Optional[User] = None


class MessageSend(BaseModel):
    content: Optional[str] = None
    embed: Optional[MessageEmbed] = None
    ark: Optional[MessageArk] = None
    markdown: Optional[MessageMarkdown] = None
    message_reference: Optional[MessageReference] = None
    keyboard: Optional[MessageKeyboard] = None
    image: Optional[str] = None
    msg_id: Optional[str] = None
    file_image: Optional[bytes] = None


class PostDmsBody(BaseModel):
    recipient_id: str
    source_guild_id: str


class PatchGuildMuteBody(BaseModel):
    mute_end_timestamp: Optional[str] = None
    mute_seconds: Optional[str] = None


class PatchGuildMemberMuteBody(BaseModel):
    mute_end_timestamp: Optional[str] = None
    mute_seconds: Optional[str] = None


class PostGuildAnnouncesBody(BaseModel):
    message_id: str
    channel_id: str


class PostChannelAnnouncesBody(BaseModel):
    message_id: str


class Announces(BaseModel):
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    message_id: Optional[str] = None


class GetSchedulesBody(BaseModel):
    since: Optional[int] = None


class ScheduleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_timestamp: int
    end_timestamp: int
    creator: Optional[Member] = None
    jump_channel_id: Optional[int] = None
    remind_type: str


class Schedule(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    start_timestamp: Optional[int] = None
    end_timestamp: Optional[int] = None
    creator: Optional[Member] = None
    jump_channel_id: Optional[int] = None
    remind_type: Optional[str] = None


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_timestamp: Optional[int] = None
    end_timestamp: Optional[int] = None
    creator: Optional[Member] = None
    jump_channel_id: Optional[int] = None
    remind_type: Optional[str] = None


class AudioControl(BaseModel):
    audio_url: Optional[str] = None
    text: Optional[str] = None
    status: Optional[int] = None


class APIPermissionDemandIdentify(BaseModel):
    path: Optional[str] = None
    name: Optional[str] = None


class PostApiPermissionDemandBody(BaseModel):
    channel_id: Optional[str] = None
    api_identify: Optional[APIPermissionDemandIdentify] = None
    desc: Optional[str] = None


class UrlGetReturn(BaseModel):
    url: Optional[str] = None


class SessionStartLimit(BaseModel):
    total: Optional[int] = None
    remaining: Optional[int] = None
    reset_after: Optional[int] = None
    max_concurrency: Optional[int] = None


class ShardUrlGetReturn(BaseModel):
    url: Optional[str] = None
    shards: Optional[int] = None
    session_start_limit: Optional[SessionStartLimit] = None


class PinsMessage(BaseModel):
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    message_ids: Optional[List[str]] = None


class MessageAudited(BaseModel):
    audit_id: Optional[str] = None
    message_id: Optional[str] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    audit_time: Optional[datetime] = None
    create_time: Optional[datetime] = None
    seq_in_channel: Optional[str] = None


class DMS(BaseModel):
    guild_id: Optional[int] = None
    channel_id: Optional[str] = None
    create_time: Optional[datetime] = None


class Emoji(BaseModel):
    id: Optional[str] = None
    type: Optional[int] = None


class ReactionTarget(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None


class MessageReaction(BaseModel):
    user_id: Optional[int] = None
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    target: Optional[ReactionTarget] = None
    emoji: Optional[Emoji] = None


class APIPermission(BaseModel):
    path: Optional[str] = None
    method: Optional[str] = None
    desc: Optional[str] = None
    auth_status: Optional[int] = None


class APIPermissionDemand(BaseModel):
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    api_identify: Optional[APIPermissionDemandIdentify] = None
    title: Optional[str] = None
    desc: Optional[str] = None


class RichType(IntEnum):
    TEXT = 1
    AT = 2
    URL = 3
    EMOJI = 4
    CHANNEL = 5
    VIDEO = 10
    IMAGE = 11


class TextInfo(BaseModel):
    text: str


class AtType(IntEnum):
    AT_EXPLICIT_USER = 1
    AT_ROLE_GROUP = 2
    AT_GUILD = 3


class AtUserInfo(BaseModel):
    id: int
    nick: str


class AtRoleInfo(BaseModel):
    role_id: int
    name: str
    color: int


class AtGuildInfo(BaseModel):
    guild_id: int
    guild_name: str


class AtInfo(BaseModel):
    type: AtType
    user_info: Optional[AtUserInfo] = None
    role_info: Optional[AtRoleInfo] = None
    guild_info: Optional[AtGuildInfo] = None


class URLInfo(BaseModel):
    url: Optional[str] = None
    display_text: Optional[str] = None


class EmojiInfo(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None


class ChannelInfo(BaseModel):
    channel_id: int
    channel_name: str


class ElemType(IntEnum):
    TEXT = 1
    IMAGE = 2
    VIDEO = 3
    URL = 4


class TextProps(BaseModel):
    font_bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None


class TextElem(BaseModel):
    text: Optional[str] = None
    props: Optional[TextProps] = None


class ImageElem(BaseModel):
    third_url: Optional[str] = None
    width_percent: Optional[float] = None


class VideoElem(BaseModel):
    third_url: Optional[str] = None


class PlatImage(BaseModel):
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    image_id: Optional[str] = None


class PlatVideo(BaseModel):
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    video_id: Optional[str] = None
    duration: Optional[int]
    cover: Optional[PlatImage]


class URLElem(BaseModel):
    url: Optional[str] = None
    desc: Optional[str] = None


class Alignment(IntEnum):
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2


class ParagraphProps(BaseModel):
    alignment: Optional[Alignment] = None


class Elem(BaseModel):
    text: Optional[TextElem] = None
    image: Optional[ImageElem] = None
    video: Optional[VideoElem] = None
    url: Optional[URLElem] = None
    type: Optional[ElemType] = None


class Paragraph(BaseModel):
    elems: Optional[List[Elem]] = None
    props: Optional[ParagraphProps] = None


class RichText(BaseModel):
    paragraphs: Optional[List[Paragraph]] = None


class RichObject(BaseModel):
    type: Optional[RichType]
    text_info: Optional[TextInfo]
    at_info: Optional[AtInfo]
    url_info: Optional[URLInfo]
    emoji_info: Optional[EmojiInfo]
    channel_info: Optional[ChannelInfo]


class ForumObjectInfo(BaseModel):
    thread_id: Optional[str] = None
    content: Optional[RichText] = None
    date_time: Optional[datetime] = None

    @validator('content', pre=True, allow_reuse=True)
    def parse_content(cls, v):
        if isinstance(v, str):
            return RichText.parse_raw(v, content_type='json')
        return v


class ForumObject(BaseModel):
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    author_id: Optional[int] = None


_T_Title = TypeVar("_T_Title", str, RichText)


class ForumThreadInfo(ForumObjectInfo, GenericModel, Generic[_T_Title]):
    # 事件推送拿到的title实际上是RichText的JSON字符串，而API调用返回的title是普通文本
    title: Optional[_T_Title] = None

    @validator('title', pre=True, allow_reuse=True)
    def parse_title(cls, v):
        if isinstance(v, str) and cls.__fields__["title"].type_ is RichText:
            return RichText.parse_raw(v, content_type='json')
        return v


class ForumThread(ForumObject, GenericModel, Generic[_T_Title]):
    thread_info: Optional[ForumThreadInfo[_T_Title]] = None


class ForumPostInfo(ForumObjectInfo):
    post_id: Optional[str] = None


class ForumPost(ForumObject):
    post_info: Optional[ForumPostInfo] = None


class ForumReplyInfo(ForumObjectInfo):
    post_id: Optional[str] = None
    reply_id: Optional[str] = None


class ForumReply(ForumObject):
    reply_info: Optional[ForumReplyInfo] = None


class ForumAuditType(IntEnum):
    PUBLISH_THREAD = 1
    PUBLISH_POST = 2
    PUBLISH_REPLY = 3


class ForumAuditResult(ForumObject):
    thread_id: Optional[int] = None
    post_id: Optional[int] = None
    reply_id: Optional[int] = None
    type: Optional[ForumAuditType] = None
    result: Optional[int] = None
    err_msg: Optional[str] = None


class GetThreadsReturn(BaseModel):
    threads: List[ForumThread[str]]
    is_finish: bool


class GetThreadReturn(BaseModel):
    thread: ForumThread[str]


class PutThreadFormat(IntEnum):
    TEXT = 1
    HTML = 2
    MARKDOWN = 3
    JSON = 4


class PutThreadBody(BaseModel):
    title: str
    content: str
    format: PutThreadFormat

    @validator("content", pre=True, allow_reuse=True)
    def convert_content(cls, v):
        if not isinstance(v, str):
            if isinstance(v, BaseModel):
                return v.json()
            else:
                return json.dumps(v)
        return v


class PutThreadReturn(BaseModel):
    task_id: int
    create_time: datetime


__all__ = [
    "Guild",
    "User",
    "ChannelCreate",
    "Channel",
    "ChannelUpdate",
    "Member",
    "DeleteMemberBody",
    "Role",
    "GetGuildRolesReturn",
    "PostGuildRoleBody",
    "GuildRole",
    "PostGuildRoleReturn",
    "PatchGuildRoleBody",
    "PatchGuildRoleReturn",
    "PutGuildMemberRoleBody",
    "DeleteGuildMemberRoleBody",
    "ChannelPermissions",
    "PutChannelPermissionsBody",
    "PutChannelRolesPermissionsBody",
    "MessageAttachment",
    "MessageEmbedThumbnail",
    "MessageEmbedField",
    "MessageEmbed",
    "MessageArkObjKv",
    "MessageArkObj",
    "MessageArkKv",
    "MessageArk",
    "MessageReference",
    "MessageMarkdownParams",
    "MessageMarkdown",
    "Permission",
    "Action",
    "RenderData",
    "Button",
    "InlineKeyboardRow",
    "InlineKeyboard",
    "MessageKeyboard",
    "Message",
    "MessageGet",
    "MessageDelete",
    "MessageSend",
    "PostDmsBody",
    "PatchGuildMuteBody",
    "PatchGuildMemberMuteBody",
    "PostGuildAnnouncesBody",
    "PostChannelAnnouncesBody",
    "Announces",
    "GetSchedulesBody",
    "ScheduleCreate",
    "Schedule",
    "ScheduleUpdate",
    "AudioControl",
    "APIPermissionDemandIdentify",
    "PostApiPermissionDemandBody",
    "UrlGetReturn",
    "SessionStartLimit",
    "ShardUrlGetReturn",
    "PinsMessage",
    "MessageAudited",
    "DMS",
    "Emoji",
    "ReactionTarget",
    "MessageReaction",
    "APIPermission",
    "APIPermissionDemand",
    "RichType",
    "TextInfo",
    "AtType",
    "AtUserInfo",
    "AtRoleInfo",
    "AtGuildInfo",
    "AtInfo",
    "URLInfo",
    "EmojiInfo",
    "ChannelInfo",
    "ElemType",
    "TextProps",
    "TextElem",
    "ImageElem",
    "VideoElem",
    "PlatImage",
    "PlatVideo",
    "URLElem",
    "Alignment",
    "ParagraphProps",
    "Elem",
    "Paragraph",
    "RichText",
    "RichObject",
    "ForumObject",
    "ForumObjectInfo",
    "ForumThreadInfo",
    "ForumThread",
    "ForumPostInfo",
    "ForumPost",
    "ForumReplyInfo",
    "ForumReply",
    "ForumAuditType",
    "ForumAuditResult",
    "GetThreadsReturn",
    "GetThreadReturn",
    "PutThreadFormat",
    "PutThreadBody",
    "PutThreadReturn"
]
