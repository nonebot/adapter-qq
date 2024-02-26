from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel

from nonebot.adapters.qq.compat import field_validator


class FriendAuthor(BaseModel):
    id: str
    user_openid: str


class GroupMemberAuthor(BaseModel):
    id: str
    member_openid: str


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
    attachments: Optional[List[Attachment]] = None


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
    members: List[GroupMember]
    next_index: Optional[int] = None


__all__ = [
    "FriendAuthor",
    "GroupMemberAuthor",
    "Attachment",
    "Media",
    "QQMessage",
    "PostC2CMessagesReturn",
    "PostGroupMessagesReturn",
    "PostC2CFilesReturn",
    "GroupMember",
    "PostGroupMembersReturn",
    "PostGroupFilesReturn",
]
