from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class Author(BaseModel):
    id: str


class PostC2CMessagesReturn(BaseModel):
    id: str
    timestamp: datetime


class PostGroupMessagesReturn(BaseModel):
    id: str
    timestamp: datetime


class PostC2CFilesReturn(BaseModel):
    id: str
    timestamp: datetime


class PostGroupFilesReturn(BaseModel):
    id: str
    timestamp: datetime


# Interaction Event
class ButtonInteractionContent(BaseModel):
    user_id: str
    message_id: str
    button_id: str
    button_data: str


class ButtonInteractionData(BaseModel):
    resolved: ButtonInteractionContent


# Interaction Event
class ButtonInteraction(BaseModel):
    id: str
    type: int
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
    "PostGroupFilesReturn",
    "ButtonInteractionContent",
    "ButtonInteractionData",
    "ButtonInteraction",
]
