from enum import Enum
from typing import Dict, Type, Tuple

from nonebot.typing import overrides
from nonebot.utils import escape_tag

from nonebot.adapters import Event as BaseEvent

from .message import Message
from .api import Message as GuildMessage
from .api import User, Guild, Member, Channel
from .api import MessageAudited, MessageReaction


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

    # GUILD_MESSAGES
    MESSAGE_CREATE = "MESSAGE_CREATE"

    # GUILD_MESSAGE_REACTIONS
    MESSAGE_REACTION_ADD = "MESSAGE_REACTION_ADD"
    MESSAGE_REACTION_REMOVE = "MESSAGE_REACTION_REMOVE"

    # DIRECT_MESSAGE
    DIRECT_MESSAGE_CREATE = "DIRECT_MESSAGE_CREATE"

    # MESSAGE_AUDIT
    MESSAGE_AUDIT_PASS = "MESSAGE_AUDIT_PASS"
    MESSAGE_AUDIT_REJECT = "MESSAGE_AUDIT_REJECT"

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
class GuildEvent(Event, Guild):
    op_user_id: str

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"


class GuildCreateEvent(GuildEvent):
    __type__ = EventType.GUILD_CREATE


class GuildUpdateEvent(GuildEvent):
    __type__ = EventType.GUILD_UPDATE


class GuildDeleteEvent(GuildEvent):
    __type__ = EventType.GUILD_DELETE


# Channel Event
class ChannelEvent(Event, Channel):
    op_user_id: str

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"


class ChannelCreateEvent(ChannelEvent):
    __type__ = EventType.CHANNEL_CREATE


class ChannelUpdateEvent(ChannelEvent):
    __type__ = EventType.CHANNEL_UPDATE


class ChannelDeleteEvent(ChannelEvent):
    __type__ = EventType.CHANNEL_DELETE


# Guild Member Event
class GuildMemberEvent(Event, Member):
    guild_id: str
    op_user_id: str

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"

    @overrides(Event)
    def get_user_id(self) -> str:
        return str(self.user.id)  # type: ignore

    @overrides(Event)
    def get_session_id(self) -> str:
        return str(self.user.id)  # type: ignore


class GuildMemberAddEvent(GuildMemberEvent):
    __type__ = EventType.GUILD_MEMBER_ADD


class GuildMemberUpdateEvent(GuildMemberEvent):
    __type__ = EventType.GUILD_MEMBER_UPDATE


class GuildMemberRemoveEvent(GuildMemberEvent):
    __type__ = EventType.GUILD_MEMBER_REMOVE


# Message Event
class MessageEvent(Event, GuildMessage):
    to_me: bool = False

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "message"

    @overrides(Event)
    def get_user_id(self) -> str:
        return str(self.author.id)  # type: ignore

    @overrides(Event)
    def get_session_id(self) -> str:
        return str(self.author.id)  # type: ignore

    @overrides(Event)
    def get_message(self) -> Message:
        if not hasattr(self, "_message"):
            setattr(self, "_message", Message.from_guild_message(self))
        return getattr(self, "_message")

    @overrides(Event)
    def is_tome(self) -> bool:
        return self.to_me


class MessageCreateEvent(MessageEvent):
    __type__ = EventType.MESSAGE_CREATE


class AtMessageCreateEvent(MessageEvent):
    __type__ = EventType.AT_MESSAGE_CREATE
    to_me: bool = True


class DirectMessageCreateEvent(MessageEvent):
    __type__ = EventType.DIRECT_MESSAGE_CREATE
    to_me: bool = True


# Message Audit Event
class MessageAuditEvent(Event, MessageAudited):
    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"


class MessageAuditPassEvent(MessageAuditEvent):
    __type__ = EventType.MESSAGE_AUDIT_PASS


class MessageAuditRejectEvent(MessageAuditEvent):
    __type__ = EventType.MESSAGE_AUDIT_REJECT


# Message Reaction Event
class MessageReactionEvent(Event, MessageReaction):
    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"

    @overrides(Event)
    def get_user_id(self) -> str:
        return str(self.user_id)

    @overrides(Event)
    def get_session_id(self) -> str:
        return str(self.user_id)


class MessageReactionAddEvent(MessageReactionEvent):
    __type__ = EventType.MESSAGE_REACTION_ADD


class MessageReactionRemoveEvent(MessageReactionEvent):
    __type__ = EventType.MESSAGE_REACTION_REMOVE


# TODO: Audio Event

event_classes: Dict[str, Type[Event]] = {
    EventType.READY.value: ReadyEvent,
    EventType.RESUMED.value: ResumedEvent,
    EventType.GUILD_CREATE.value: GuildCreateEvent,
    EventType.GUILD_DELETE.value: GuildDeleteEvent,
    EventType.GUILD_UPDATE.value: GuildUpdateEvent,
    EventType.CHANNEL_CREATE.value: ChannelCreateEvent,
    EventType.CHANNEL_DELETE.value: ChannelDeleteEvent,
    EventType.CHANNEL_UPDATE.value: ChannelUpdateEvent,
    EventType.GUILD_MEMBER_ADD.value: GuildMemberAddEvent,
    EventType.GUILD_MEMBER_UPDATE.value: GuildMemberUpdateEvent,
    EventType.GUILD_MEMBER_REMOVE.value: GuildMemberRemoveEvent,
    EventType.MESSAGE_CREATE.value: MessageCreateEvent,
    EventType.AT_MESSAGE_CREATE.value: AtMessageCreateEvent,
    EventType.DIRECT_MESSAGE_CREATE.value: DirectMessageCreateEvent,
    EventType.MESSAGE_AUDIT_PASS.value: MessageAuditPassEvent,
    EventType.MESSAGE_AUDIT_REJECT.value: MessageAuditRejectEvent,
    EventType.MESSAGE_REACTION_ADD.value: MessageReactionAddEvent,
    EventType.MESSAGE_REACTION_REMOVE.value: MessageReactionRemoveEvent,
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
