from typing import Optional
from datetime import datetime
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


__all__ = [
    "Attachment",
    "FriendAuthor",
    "GroupMember",
    "GroupMemberAuthor",
    "Media",
    "PostC2CFilesReturn",
    "PostC2CMessagesReturn",
    "PostGroupFilesReturn",
    "PostGroupMembersReturn",
    "PostGroupMessagesReturn",
    "QQMessage",
]
