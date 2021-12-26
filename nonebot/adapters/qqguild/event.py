from enum import Enum

from nonebot.adapters import Event as BaseEvent


class EventType(Enum):
    # Init Event
    READY = "READY"
    RESUMED = "RESUMED"

    # AT_MESSAGES
    AT_MESSAGE_CREATE = "AT_MESSAGE_CREATE"


class Event(BaseEvent):
    ...
