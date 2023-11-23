from typing import List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, validator


# Message Attachment
class MessageAttachment(BaseModel):
    url: str

    @validator("url", allow_reuse=True)
    def check_url(cls, v: str):
        if v and not urlparse(v).hostname:
            return f"https://{v}"
        return v


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
    unsupport_tips: Optional[str] = None
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
    rows: Optional[List[InlineKeyboardRow]] = None


class MessageKeyboard(BaseModel):
    id: Optional[str] = None
    content: Optional[InlineKeyboard] = None


__all__ = [
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
]
