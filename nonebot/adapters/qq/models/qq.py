from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


class Author(BaseModel):
    id: str


class PostC2CMessagesReturn(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[datetime] = None


class PostGroupMessagesReturn(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[datetime] = None


class PostC2CFilesReturn(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[datetime] = None


class PostGroupFilesReturn(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[datetime] = None


class GroupMember(BaseModel):
    member_openid: str
    join_timestamp: datetime


class PostGroupMembersReturn(BaseModel):
    members: List[GroupMember]
    next_index: Optional[int] = None


# Interaction Event
class ButtonInteractionContent(BaseModel):
    user_id: str
    message_id: str
    button_id: str
    button_data: str


class ButtonInteractionData(BaseModel):
    resolved: ButtonInteractionContent


class ButtonInteraction(BaseModel):
    id: str
    type: Literal[11]
    version: int
    timestamp: str
    chat_type: int
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    group_open_id: Optional[str] = None
    application_id: str
    data: ButtonInteractionData


__all__ = [
    "Author",
    "PostC2CMessagesReturn",
    "PostGroupMessagesReturn",
    "PostC2CFilesReturn",
    "GroupMember",
    "PostGroupMembersReturn",
    "PostGroupFilesReturn",
    "ButtonInteractionContent",
    "ButtonInteractionData",
    "ButtonInteraction",
]
