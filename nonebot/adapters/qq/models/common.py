from datetime import datetime
from typing import Literal
from urllib.parse import urlparse

from nonebot.compat import field_validator
from pydantic import BaseModel


# Message Attachment
class MessageAttachment(BaseModel):
    url: str

    @field_validator("url", mode="after")
    @classmethod
    def check_url(cls, v: str):
        if v and not urlparse(v).hostname:
            return f"https://{v}"
        return v


# Message Embed
class MessageEmbedThumbnail(BaseModel):
    url: str


class MessageEmbedField(BaseModel):
    name: str | None = None


class MessageEmbed(BaseModel):
    title: str | None = None
    description: str | None = None
    prompt: str
    thumbnail: MessageEmbedThumbnail | None = None
    fields: list[MessageEmbedField] | None = None


# Message Ark
class MessageArkObjKv(BaseModel):
    key: str | None = None
    value: str | None = None


class MessageArkObj(BaseModel):
    obj_kv: list[MessageArkObjKv] | None = None


class MessageArkKv(BaseModel):
    key: str | None = None
    value: str | None = None
    obj: list[MessageArkObj] | None = None


class MessageArk(BaseModel):
    template_id: int | None = None
    kv: list[MessageArkKv] | None = None


# Message Reference
class MessageReference(BaseModel):
    message_id: str
    ignore_get_message_error: bool | None = None


# Message Markdown
class MessageMarkdownParams(BaseModel):
    key: str | None = None
    values: list[str] | None = None


class MessageMarkdown(BaseModel):
    template_id: int | None = None
    custom_template_id: str | None = None
    params: list[MessageMarkdownParams] | None = None
    content: str | None = None


# Message Keyboard
class Permission(BaseModel):
    type: int | None = None
    specify_role_ids: list[str] | None = None
    specify_user_ids: list[str] | None = None


class Action(BaseModel):
    type: int | None = None
    permission: Permission | None = None
    data: str | None = None
    reply: bool | None = None
    enter: bool | None = None
    anchor: int | None = None
    unsupport_tips: str | None = None
    click_limit: int | None = None  # deprecated
    at_bot_show_channel_list: bool | None = None  # deprecated


class RenderData(BaseModel):
    label: str | None = None
    visited_label: str | None = None
    style: int | None = None


class Button(BaseModel):
    id: str | None = None
    render_data: RenderData | None = None
    action: Action | None = None


class InlineKeyboardRow(BaseModel):
    buttons: list[Button] | None = None


class InlineKeyboard(BaseModel):
    rows: list[InlineKeyboardRow] | None = None


class MessageKeyboard(BaseModel):
    id: str | None = None
    content: InlineKeyboard | None = None


# Message Audit Event
class MessageAudited(BaseModel):
    audit_id: str
    message_id: str | None = None
    user_openid: str | None = None
    group_openid: str | None = None
    guild_id: str | None = None
    channel_id: str | None = None
    audit_time: datetime
    create_time: datetime | None = None
    seq_in_channel: str | None = None


# Interaction Event
class ButtonInteractionContent(BaseModel):
    user_id: str | None = None
    message_id: str | None = None
    feature_id: str | None = None
    button_id: str | None = None
    button_data: str | None = None
    checked: int | None = None
    feedback_opt: str | None = None


class ButtonInteractionData(BaseModel):
    resolved: ButtonInteractionContent


class ButtonInteraction(BaseModel):
    id: str
    type: Literal[11, 12, 13]
    version: int
    timestamp: str
    scene: str
    chat_type: int
    guild_id: str | None = None
    channel_id: str | None = None
    user_openid: str | None = None
    group_openid: str | None = None
    group_member_openid: str | None = None
    application_id: str
    data: ButtonInteractionData


__all__ = [
    "Action",
    "Button",
    "ButtonInteraction",
    "ButtonInteractionContent",
    "ButtonInteractionData",
    "InlineKeyboard",
    "InlineKeyboardRow",
    "MessageArk",
    "MessageArkKv",
    "MessageArkObj",
    "MessageArkObjKv",
    "MessageAttachment",
    "MessageAudited",
    "MessageEmbed",
    "MessageEmbedField",
    "MessageEmbedThumbnail",
    "MessageKeyboard",
    "MessageMarkdown",
    "MessageMarkdownParams",
    "MessageReference",
    "Permission",
    "RenderData",
]
