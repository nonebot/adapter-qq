from datetime import datetime
from typing import Literal, Optional
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
    template_id: Literal["1", "10"] = "1"  # 待废弃字段！！！
    callback_data: Optional[str] = None
    feedback: Optional[bool] = None  # 反馈按钮（赞踩按钮）
    tts: Optional[bool] = None  # TTS 语音播放按钮
    re_generate: Optional[bool] = None  # 重新生成按钮
    stop_generate: Optional[bool] = None  # 停止生成按钮


class PromptAction(BaseModel):
    type: Literal[2] = 2


class PromptRenderData(BaseModel):
    label: str
    style: Literal[2] = 2


class PromptButton(BaseModel):
    render_data: PromptRenderData
    action: PromptAction


class PromptRow(BaseModel):
    buttons: list[PromptButton]


class PromptContent(BaseModel):
    rows: list[PromptRow]


class PromptKeyboardModel(BaseModel):
    content: PromptContent


class MessagePromptKeyboard(BaseModel):
    keyboard: PromptKeyboardModel


class MessageStream(BaseModel):
    state: Literal[1, 10, 11, 20]
    """1: 正文生成中, 10: 正文生成结束, 11: 引志消息生成中, 20: 引导消息生成结束。"""
    id: Optional[str] = None
    """第一条不用填写，第二条需要填写第一个分片返回的 msgID"""
    index: int
    """从 1 开始"""
    reset: Optional[bool] = None
    """只能用于流式消息没有发送完成时，reset 时 index 需要从 0 开始，需要填写流式 id"""


__all__ = [
    "Attachment",
    "FriendAuthor",
    "GroupMember",
    "GroupMemberAuthor",
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
    "PromptKeyboardModel",
    "PromptRenderData",
    "PromptRow",
    "QQMessage",
]
