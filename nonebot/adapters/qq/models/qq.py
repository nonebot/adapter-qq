from datetime import datetime
from typing import List, Literal, Optional
from urllib.parse import urlparse

from pydantic import BaseModel

from nonebot.adapters.qq.compat import field_validator


class FriendAuthor(BaseModel):
    id: str
    user_openid: str
    union_openid: Optional[str] = None


class GroupMemberAuthor(BaseModel):
    id: str
    member_openid: str
    union_openid: Optional[str] = None


class Attachment(BaseModel):
    content_type: str
    filename: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
    size: Optional[int] = None
    url: Optional[str] = None

    @field_validator("url", mode="after")
    def check_url(cls, v: str):
        if v and not urlparse(v).hostname:
            return f"https://{v}"
        return v


class Media(BaseModel):
    file_info: str


class QQMessage(BaseModel):
    id: str
    content: str
    timestamp: str
    attachments: Optional[list[Attachment]] = None


class PostC2CMessagesReturn(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[datetime] = None


class PostGroupMessagesReturn(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[datetime] = None


class PostC2CFilesReturn(BaseModel):
    file_uuid: Optional[str] = None
    file_info: Optional[str] = None
    ttl: Optional[int] = None


class PostGroupFilesReturn(BaseModel):
    file_uuid: Optional[str] = None
    file_info: Optional[str] = None
    ttl: Optional[int] = None


class GroupMember(BaseModel):
    member_openid: str
    join_timestamp: datetime


class PostGroupMembersReturn(BaseModel):
    members: list[GroupMember]
    next_index: Optional[int] = None


class MessageActionButton(BaseModel):
    template_id: Literal["1", "10"] = "1"
    callback_data: Optional[str] = None


class PromptAction(BaseModel):
    type: Literal[2] = 2


class PromptRenderData(BaseModel):
    label: str
    style: Literal[2] = 2


class PromptButton(BaseModel):
    render_data: str
    action: PromptAction


class PromptRow(BaseModel):
    buttons: List[PromptButton]


class PromptContent(BaseModel):
    rows: List[PromptRow]


class Keyboard(BaseModel):
    content: PromptContent


class MessagePromptKeyboard(BaseModel):
    keyboard: Keyboard


class MessageStream(BaseModel):
    state: Literal[1, 10, 11]
    id: str  # msg_id
    index: int


__all__ = [
    "Attachment",
    "FriendAuthor",
    "GroupMember",
    "GroupMemberAuthor",
    "Keyboard",
    "Media",
    "MessageActionButton",
    "MessagePromptKeyboard",
    "MessageStream",
    "PostC2CFilesReturn",
    "PostC2CMessagesReturn",
    "PostGroupFilesReturn",
    "PostGroupMembersReturn",
    "PostGroupMessagesReturn",
    "PromptAction",
    "PromptButton",
    "PromptContent",
    "PromptRenderData",
    "PromptRow",
    "QQMessage",
]
