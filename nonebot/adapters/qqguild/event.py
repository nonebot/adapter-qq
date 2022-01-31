from enum import Enum
from typing import Dict, Type, Tuple

from nonebot.typing import overrides
from nonebot.utils import escape_tag

from nonebot.adapters import Event as BaseEvent

from .message import Message
from .model import BaseChannel
from .model import User, Guild
from .model import Message as GuildMessage


class EventType(str, Enum):
    # Init Event
    READY = "READY"
    RESUMED = "RESUMED"

    # GUILDS
    GUILD_CREATE = "GUILD_CREATE"
    GUILD_UPDATE = "GUILD_UPDATE"
    GUILD_DELETE = "GUILD_DELETE"
    CHANNEL_CREATE = "CHANNEL_CREATE"
    CHANNEL_UPDATE = "CHANNEL_UPDATE"
    CHANNEL_DELETE = "CHANNEL_DELETE"

    # GUILD_MEMBERS
    GUILD_MEMBER_ADD = "GUILD_MEMBER_ADD"
    GUILD_MEMBER_UPDATE = "GUILD_MEMBER_UPDATE"
    GUILD_MEMBER_REMOVE = "GUILD_MEMBER_REMOVE"

    # GUILD_MESSAGE_REACTIONS
    MESSAGE_REACTION_ADD = "MESSAGE_REACTION_ADD"
    MESSAGE_REACTION_REMOVE = "MESSAGE_REACTION_REMOVE"

    # DIRECT_MESSAGE
    DIRECT_MESSAGE_CREATE = "DIRECT_MESSAGE_CREATE"

    # FORUM_EVENT
    THREAD_CREATE = "THREAD_CREATE"
    THREAD_UPDATE = "THREAD_UPDATE"
    THREAD_DELETE = "THREAD_DELETE"
    POST_CREATE = "POST_CREATE"
    POST_DELETE = "POST_DELETE"
    REPLY_CREATE = "REPLY_CREATE"
    REPLY_DELETE = "REPLY_DELETE"

    # AUDIO_ACTION
    AUDIO_START = "AUDIO_START"
    AUDIO_FINISH = "AUDIO_FINISH"
    AUDIO_ON_MIC = "AUDIO_ON_MIC"
    AUDIO_OFF_MIC = "AUDIO_OFF_MIC"

    # AT_MESSAGES
    AT_MESSAGE_CREATE = "AT_MESSAGE_CREATE"


class Event(BaseEvent):
    __type__: EventType

    @overrides(BaseEvent)
    def get_event_name(self) -> str:
        return self.__type__

    @overrides(BaseEvent)
    def get_event_description(self) -> str:
        return escape_tag(str(self.dict()))

    @overrides(BaseEvent)
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_user_id(self) -> str:
        raise ValueError("Event has no context!")

    @overrides(BaseEvent)
    def get_session_id(self) -> str:
        raise ValueError("Event has no context!")

    @overrides(BaseEvent)
    def is_tome(self) -> bool:
        return False


# Meta Event
class MetaEvent(Event):
    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "meta_event"


class ReadyEvent(MetaEvent):
    __type__ = EventType.READY
    version: int
    session_id: str
    user: User
    shard: Tuple[int, int]


class ResumedEvent(MetaEvent):
    __type__ = EventType.RESUMED


# Guild Event
class GuildEvent(Event):
    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"


class GuildCreateEvent(GuildEvent, Guild):
    __type__ = EventType.GUILD_CREATE


class GuildUpdateEvent(GuildEvent, Guild):
    __type__ = EventType.GUILD_UPDATE


class GuildDeleteEvent(GuildEvent, Guild):
    __type__ = EventType.GUILD_DELETE


# Channel Event
class ChannelEvent(Event):
    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"


class ChannelCreateEvent(ChannelEvent, BaseChannel):
    __type__ = EventType.CHANNEL_CREATE


class ChannelUpdateEvent(ChannelEvent, BaseChannel):
    __type__ = EventType.CHANNEL_UPDATE


class ChannelDeleteEvent(ChannelEvent, BaseChannel):
    __type__ = EventType.CHANNEL_DELETE


# Guild Member Event

# Message Event
class MessageEvent(Event):
    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "message"


class AtMessageCreateEvent(MessageEvent, GuildMessage):
    __type__ = EventType.AT_MESSAGE_CREATE
    content: Message

    @overrides(Event)
    def get_message(self) -> Message:
        return self.content


# Message Reaction Event

# Audio Event

event_classes: Dict[str, Type[Event]] = {
    EventType.READY.value: ReadyEvent,
    EventType.RESUMED.value: ResumedEvent,
    EventType.GUILD_CREATE.value: GuildCreateEvent,
    EventType.GUILD_DELETE.value: GuildDeleteEvent,
    EventType.GUILD_UPDATE.value: GuildUpdateEvent,
    EventType.CHANNEL_CREATE.value: ChannelCreateEvent,
    EventType.CHANNEL_DELETE.value: ChannelDeleteEvent,
    EventType.CHANNEL_UPDATE.value: ChannelUpdateEvent,
    EventType.AT_MESSAGE_CREATE.value: AtMessageCreateEvent,
}

__all__ = [
    "EventType",
    "Event",
    "GuildEvent",
    "GuildCreateEvent",
    "GuildUpdateEvent",
    "GuildDeleteEvent",
    "ChannelEvent",
    "ChannelCreateEvent",
    "ChannelUpdateEvent",
    "ChannelDeleteEvent",
    "MessageEvent",
    "AtMessageCreateEvent",
]
