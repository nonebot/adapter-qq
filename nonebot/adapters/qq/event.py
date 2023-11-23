from enum import Enum
from datetime import datetime
from typing_extensions import override
from typing import Dict, Type, Tuple, TypeVar, Optional

from nonebot.utils import escape_tag

from nonebot.adapters import Event as BaseEvent

from .message import Message
from .models import Message as GuildMessage
from .models import Post, User, Guild, Reply, Member, Thread, Channel
from .models import (
    RichText,
    QQMessage,
    AudioAction,
    FriendAuthor,
    MessageDelete,
    MessageAudited,
    ForumSourceInfo,
    MessageReaction,
    ForumAuditResult,
    ButtonInteraction,
    GroupMemberAuthor,
)

E = TypeVar("E", bound="Event")


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
    MESSAGE_DELETE = "MESSAGE_DELETE"

    # GUILD_MESSAGE_REACTIONS
    MESSAGE_REACTION_ADD = "MESSAGE_REACTION_ADD"
    MESSAGE_REACTION_REMOVE = "MESSAGE_REACTION_REMOVE"

    # DIRECT_MESSAGE
    DIRECT_MESSAGE_CREATE = "DIRECT_MESSAGE_CREATE"
    DIRECT_MESSAGE_DELETE = "DIRECT_MESSAGE_DELETE"

    # OPEN_FORUMS_EVENT
    OPEN_FORUM_THREAD_CREATE = "OPEN_FORUM_THREAD_CREATE"
    OPEN_FORUM_THREAD_UPDATE = "OPEN_FORUM_THREAD_UPDATE"
    OPEN_FORUM_THREAD_DELETE = "OPEN_FORUM_THREAD_DELETE"
    OPEN_FORUM_POST_CREATE = "OPEN_FORUM_POST_CREATE"
    OPEN_FORUM_POST_DELETE = "OPEN_FORUM_POST_DELETE"
    OPEN_FORUM_REPLY_CREATE = "OPEN_FORUM_REPLY_CREATE"
    OPEN_FORUM_REPLY_DELETE = "OPEN_FORUM_REPLY_DELETE"

    # AUDIO_OR_LIVE_CHANNEL_MEMBER
    AUDIO_OR_LIVE_CHANNEL_MEMBER_ENTER = "AUDIO_OR_LIVE_CHANNEL_MEMBER_ENTER"
    AUDIO_OR_LIVE_CHANNEL_MEMBER_EXIT = "AUDIO_OR_LIVE_CHANNEL_MEMBER_EXIT"

    # C2C_GROUP_AT_MESSAGES
    C2C_MESSAGE_CREATE = "C2C_MESSAGE_CREATE"
    GROUP_AT_MESSAGE_CREATE = "GROUP_AT_MESSAGE_CREATE"

    # INTERACTION
    INTERACTION_CREATE = "INTERACTION_CREATE"

    # MESSAGE_AUDIT
    MESSAGE_AUDIT_PASS = "MESSAGE_AUDIT_PASS"
    MESSAGE_AUDIT_REJECT = "MESSAGE_AUDIT_REJECT"

    # FORUM_EVENT
    FORUM_THREAD_CREATE = "FORUM_THREAD_CREATE"
    FORUM_THREAD_UPDATE = "FORUM_THREAD_UPDATE"
    FORUM_THREAD_DELETE = "FORUM_THREAD_DELETE"
    FORUM_POST_CREATE = "FORUM_POST_CREATE"
    FORUM_POST_DELETE = "FORUM_POST_DELETE"
    FORUM_REPLY_CREATE = "FORUM_REPLY_CREATE"
    FORUM_REPLY_DELETE = "FORUM_REPLY_DELETE"
    FORUM_PUBLISH_AUDIT_RESULT = "FORUM_PUBLISH_AUDIT_RESULT"

    # AUDIO_ACTION
    AUDIO_START = "AUDIO_START"
    AUDIO_FINISH = "AUDIO_FINISH"
    AUDIO_ON_MIC = "AUDIO_ON_MIC"
    AUDIO_OFF_MIC = "AUDIO_OFF_MIC"

    # AT_MESSAGES
    AT_MESSAGE_CREATE = "AT_MESSAGE_CREATE"
    PUBLIC_MESSAGE_DELETE = "PUBLIC_MESSAGE_DELETE"

    # FRIEND_ROBOT_EVENT
    FRIEND_ADD = "FRIEND_ADD"
    FRIEND_DEL = "FRIEND_DEL"
    C2C_MSG_REJECT = "C2C_MSG_REJECT"
    C2C_MSG_RECEIVE = "C2C_MSG_RECEIVE"

    # GROUP_ROBOT_EVENT
    GROUP_ADD_ROBOT = "GROUP_ADD_ROBOT"
    GROUP_DEL_ROBOT = "GROUP_DEL_ROBOT"
    GROUP_MSG_REJECT = "GROUP_MSG_REJECT"
    GROUP_MSG_RECEIVE = "GROUP_MSG_RECEIVE"


class Event(BaseEvent):
    __type__: EventType

    @override
    def get_event_name(self) -> str:
        return self.__type__

    @override
    def get_event_description(self) -> str:
        return escape_tag(str(self.dict()))

    @override
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @override
    def get_user_id(self) -> str:
        raise ValueError("Event has no context!")

    @override
    def get_session_id(self) -> str:
        raise ValueError("Event has no context!")

    @override
    def is_tome(self) -> bool:
        return False


EVENT_CLASSES: Dict[str, Type[Event]] = {}


def register_event_class(event_class: Type[E]) -> Type[E]:
    EVENT_CLASSES[event_class.__type__.value] = event_class
    return event_class


# Meta Event
class MetaEvent(Event):
    @override
    def get_type(self) -> str:
        return "meta_event"


@register_event_class
class ReadyEvent(MetaEvent):
    __type__ = EventType.READY
    version: int
    session_id: str
    user: User
    shard: Tuple[int, int]


@register_event_class
class ResumedEvent(MetaEvent):
    __type__ = EventType.RESUMED


# Notice Event
class NoticeEvent(Event):
    @override
    def get_type(self) -> str:
        return "notice"


# Guild Event
class GuildEvent(NoticeEvent, Guild):
    op_user_id: str


@register_event_class
class GuildCreateEvent(GuildEvent):
    __type__ = EventType.GUILD_CREATE


@register_event_class
class GuildUpdateEvent(GuildEvent):
    __type__ = EventType.GUILD_UPDATE


@register_event_class
class GuildDeleteEvent(GuildEvent):
    __type__ = EventType.GUILD_DELETE


# Channel Event
class ChannelEvent(NoticeEvent, Channel):
    op_user_id: str


@register_event_class
class ChannelCreateEvent(ChannelEvent):
    __type__ = EventType.CHANNEL_CREATE


@register_event_class
class ChannelUpdateEvent(ChannelEvent):
    __type__ = EventType.CHANNEL_UPDATE


@register_event_class
class ChannelDeleteEvent(ChannelEvent):
    __type__ = EventType.CHANNEL_DELETE


# Guild Member Event
class GuildMemberEvent(NoticeEvent, Member):
    guild_id: str
    op_user_id: str

    @override
    def get_user_id(self) -> str:
        return self.user.id  # type: ignore

    @override
    def get_event_description(self) -> str:
        return escape_tag(
            f"Notice {getattr(self.user, 'username', None)}"
            f"@[Guild:{self.guild_id}] Roles:{self.roles}"
        )

    @override
    def get_session_id(self) -> str:
        return f"guild_{self.guild_id}_{self.user.id}"  # type: ignore


@register_event_class
class GuildMemberAddEvent(GuildMemberEvent):
    __type__ = EventType.GUILD_MEMBER_ADD


@register_event_class
class GuildMemberUpdateEvent(GuildMemberEvent):
    __type__ = EventType.GUILD_MEMBER_UPDATE


@register_event_class
class GuildMemberRemoveEvent(GuildMemberEvent):
    __type__ = EventType.GUILD_MEMBER_REMOVE


# Message Event
class MessageEvent(Event):
    to_me: bool = False

    @override
    def get_type(self) -> str:
        return "message"

    @override
    def is_tome(self) -> bool:
        return self.to_me


class GuildMessageEvent(MessageEvent, GuildMessage):
    reply: Optional[GuildMessage] = None
    """
    :说明: 消息中提取的回复消息，内容为 ``get_message_of_id`` API 返回结果

    :类型: ``Optional[GuildMessage]``
    """

    @override
    def get_user_id(self) -> str:
        return self.author.id

    @override
    def get_session_id(self) -> str:
        return f"guild_{self.guild_id}_channel_{self.channel_id}_{self.author.id}"

    @override
    def get_event_description(self) -> str:
        return escape_tag(
            f"Message {self.id} from "
            f"{getattr(self.author, 'username', None)}"
            f"@[Guild:{self.guild_id}/{self.channel_id}] "
            f"Roles:{getattr(self.member, 'roles', None)}: {self.get_message()!r}"
        )

    @override
    def get_message(self) -> Message:
        if not hasattr(self, "_message"):
            setattr(self, "_message", Message.from_guild_message(self))
        return getattr(self, "_message")


@register_event_class
class MessageCreateEvent(GuildMessageEvent):
    __type__ = EventType.MESSAGE_CREATE


@register_event_class
class MessageDeleteEvent(NoticeEvent, MessageDelete):
    __type__ = EventType.MESSAGE_DELETE

    @override
    def get_session_id(self) -> str:
        return (
            f"guild_{self.message.guild_id}_"
            f"channel_{self.message.channel_id}_{self.op_user.id}"
        )


@register_event_class
class AtMessageCreateEvent(GuildMessageEvent):
    __type__ = EventType.AT_MESSAGE_CREATE

    to_me: bool = True


@register_event_class
class PublicMessageDeleteEvent(MessageDeleteEvent):
    __type__ = EventType.PUBLIC_MESSAGE_DELETE


@register_event_class
class DirectMessageCreateEvent(GuildMessageEvent):
    __type__ = EventType.DIRECT_MESSAGE_CREATE

    to_me: bool = True

    @override
    def get_event_description(self) -> str:
        return escape_tag(
            f"Message {self.id} from "
            f"{getattr(self.author, 'username', None)}: {self.get_message()!r}"
        )


@register_event_class
class DirectMessageDeleteEvent(MessageDeleteEvent):
    __type__ = EventType.DIRECT_MESSAGE_DELETE


class QQMessageEvent(MessageEvent, QQMessage):
    _reply_seq: int = -1

    @override
    def get_message(self) -> Message:
        if not hasattr(self, "_message"):
            setattr(self, "_message", Message.from_qq_message(self))
        return getattr(self, "_message")


@register_event_class
class C2CMessageCreateEvent(QQMessageEvent):
    __type__ = EventType.C2C_MESSAGE_CREATE

    author: FriendAuthor
    to_me: bool = True

    @override
    def get_user_id(self) -> str:
        return self.author.user_openid

    @override
    def get_session_id(self) -> str:
        return f"friend_{self.author.user_openid}"

    @override
    def get_event_description(self) -> str:
        return escape_tag(
            f"Message {self.id} from {self.author.id}: {self.get_message()!r}"
        )


@register_event_class
class GroupAtMessageCreateEvent(QQMessageEvent):
    __type__ = EventType.GROUP_AT_MESSAGE_CREATE

    author: GroupMemberAuthor
    group_openid: str
    to_me: bool = True

    @override
    def get_user_id(self) -> str:
        return self.author.member_openid

    @override
    def get_session_id(self) -> str:
        return f"group_{self.group_openid}_{self.author.member_openid}"

    @override
    def get_event_description(self) -> str:
        return escape_tag(
            f"Message {self.id} from "
            f"{self.author.member_openid}@[Group:{self.group_openid}]: "
            f"{self.get_message()!r}"
        )


@register_event_class
class InteractionCreateEvent(NoticeEvent, ButtonInteraction):
    __type__ = EventType.INTERACTION_CREATE

    @override
    def get_user_id(self) -> str:
        return self.data.resolved.user_id

    @override
    def get_session_id(self) -> str:
        return (
            f"guild_{self.guild_id}_channel_{self.channel_id}"
            f"_{self.data.resolved.user_id}"
        )


# Message Audit Event
class MessageAuditEvent(NoticeEvent, MessageAudited):
    ...


@register_event_class
class MessageAuditPassEvent(MessageAuditEvent):
    __type__ = EventType.MESSAGE_AUDIT_PASS


@register_event_class
class MessageAuditRejectEvent(MessageAuditEvent):
    __type__ = EventType.MESSAGE_AUDIT_REJECT


# Message Reaction Event
class MessageReactionEvent(NoticeEvent, MessageReaction):
    @override
    def get_user_id(self) -> str:
        return self.user_id

    @override
    def get_session_id(self) -> str:
        return f"guild_{self.guild_id}_channel_{self.channel_id}_{self.user_id}"


@register_event_class
class MessageReactionAddEvent(MessageReactionEvent):
    __type__ = EventType.MESSAGE_REACTION_ADD


@register_event_class
class MessageReactionRemoveEvent(MessageReactionEvent):
    __type__ = EventType.MESSAGE_REACTION_REMOVE


# Audio Event
class AudioEvent(NoticeEvent, AudioAction):
    ...


@register_event_class
class AudioStartEvent(AudioEvent):
    __type__ = EventType.AUDIO_START


@register_event_class
class AudioFinishEvent(AudioEvent):
    __type__ = EventType.AUDIO_FINISH


@register_event_class
class AudioOnMicEvent(AudioEvent):
    __type__ = EventType.AUDIO_ON_MIC


@register_event_class
class AudioOffMicEvent(AudioEvent):
    __type__ = EventType.AUDIO_OFF_MIC


# Forum Event
class ForumEvent(NoticeEvent, ForumSourceInfo):
    @override
    def get_user_id(self) -> str:
        return self.author_id

    @override
    def get_session_id(self) -> str:
        return f"guild_{self.guild_id}_channel_{self.channel_id}_{self.author_id}"


class ForumThreadEvent(ForumEvent, Thread[RichText]):
    ...


@register_event_class
class ForumThreadCreateEvent(ForumThreadEvent):
    __type__ = EventType.FORUM_THREAD_CREATE


@register_event_class
class ForumThreadUpdateEvent(ForumThreadEvent):
    __type__ = EventType.FORUM_THREAD_UPDATE


@register_event_class
class ForumThreadDeleteEvent(ForumThreadEvent):
    __type__ = EventType.FORUM_THREAD_DELETE


class ForumPostEvent(ForumEvent, Post):
    ...


@register_event_class
class ForumPostCreateEvent(ForumPostEvent):
    __type__ = EventType.FORUM_POST_CREATE


@register_event_class
class ForumPostDeleteEvent(ForumPostEvent):
    __type__ = EventType.FORUM_POST_DELETE


class ForumReplyEvent(ForumEvent, Reply):
    ...


@register_event_class
class ForumReplyCreateEvent(ForumReplyEvent):
    __type__ = EventType.FORUM_REPLY_CREATE


@register_event_class
class ForumReplyDeleteEvent(ForumReplyEvent):
    __type__ = EventType.FORUM_REPLY_DELETE


@register_event_class
class ForumPublishAuditResult(ForumEvent, ForumAuditResult):
    __type__ = EventType.FORUM_PUBLISH_AUDIT_RESULT


class OpenForumEvent(NoticeEvent, ForumSourceInfo):
    @override
    def get_user_id(self) -> str:
        return self.author_id

    @override
    def get_session_id(self) -> str:
        return f"guild_{self.guild_id}_channel_{self.channel_id}_{self.author_id}"


@register_event_class
class OpenForumThreadCreateEvent(OpenForumEvent):
    __type__ = EventType.OPEN_FORUM_THREAD_CREATE


@register_event_class
class OpenForumThreadUpdateEvent(OpenForumEvent):
    __type__ = EventType.OPEN_FORUM_THREAD_UPDATE


@register_event_class
class OpenForumThreadDeleteEvent(OpenForumEvent):
    __type__ = EventType.OPEN_FORUM_THREAD_DELETE


@register_event_class
class OpenForumPostCreateEvent(OpenForumEvent):
    __type__ = EventType.OPEN_FORUM_POST_CREATE


@register_event_class
class OpenForumPostDeleteEvent(OpenForumEvent):
    __type__ = EventType.OPEN_FORUM_POST_DELETE


@register_event_class
class OpenForumReplyCreateEvent(OpenForumEvent):
    __type__ = EventType.OPEN_FORUM_REPLY_CREATE


@register_event_class
class OpenForumReplyDeleteEvent(OpenForumEvent):
    __type__ = EventType.OPEN_FORUM_REPLY_DELETE


# Friend Robot Event
class FriendRobotEvent(NoticeEvent):
    timestamp: datetime
    openid: str

    @override
    def get_user_id(self) -> str:
        return self.openid

    @override
    def get_session_id(self) -> str:
        return f"friend_{self.openid}"


@register_event_class
class FriendAddEvent(FriendRobotEvent):
    __type__ = EventType.FRIEND_ADD


@register_event_class
class FriendDelEvent(FriendRobotEvent):
    __type__ = EventType.FRIEND_DEL


@register_event_class
class C2CMsgRejectEvent(FriendRobotEvent):
    __type__ = EventType.C2C_MSG_REJECT


@register_event_class
class C2CMsgReceiveEvent(FriendRobotEvent):
    __type__ = EventType.C2C_MSG_RECEIVE


# Group Robot Event
class GroupRobotEvent(NoticeEvent):
    timestamp: datetime
    group_openid: str
    op_member_openid: str

    @override
    def get_user_id(self) -> str:
        return self.op_member_openid

    @override
    def get_session_id(self) -> str:
        return f"group_{self.group_openid}_{self.op_member_openid}"


@register_event_class
class GroupAddRobotEvent(GroupRobotEvent):
    __type__ = EventType.GROUP_ADD_ROBOT


@register_event_class
class GroupDelRobotEvent(GroupRobotEvent):
    __type__ = EventType.GROUP_DEL_ROBOT


@register_event_class
class GroupMsgRejectEvent(GroupRobotEvent):
    __type__ = EventType.GROUP_MSG_REJECT


@register_event_class
class GroupMsgReceiveEvent(GroupRobotEvent):
    __type__ = EventType.GROUP_MSG_RECEIVE


__all__ = [
    "EVENT_CLASSES",
    "EventType",
    "Event",
    "MetaEvent",
    "ReadyEvent",
    "ResumedEvent",
    "NoticeEvent",
    "GuildEvent",
    "GuildCreateEvent",
    "GuildUpdateEvent",
    "GuildDeleteEvent",
    "ChannelEvent",
    "ChannelCreateEvent",
    "ChannelUpdateEvent",
    "ChannelDeleteEvent",
    "GuildMemberEvent",
    "GuildMemberAddEvent",
    "GuildMemberUpdateEvent",
    "GuildMemberRemoveEvent",
    "MessageEvent",
    "GuildMessageEvent",
    "MessageCreateEvent",
    "MessageDeleteEvent",
    "AtMessageCreateEvent",
    "PublicMessageDeleteEvent",
    "DirectMessageCreateEvent",
    "DirectMessageDeleteEvent",
    "QQMessageEvent",
    "C2CMessageCreateEvent",
    "GroupAtMessageCreateEvent",
    "InteractionCreateEvent",
    "MessageAuditEvent",
    "MessageAuditPassEvent",
    "MessageAuditRejectEvent",
    "MessageReactionEvent",
    "MessageReactionAddEvent",
    "MessageReactionRemoveEvent",
    "AudioEvent",
    "AudioStartEvent",
    "AudioFinishEvent",
    "AudioOnMicEvent",
    "AudioOffMicEvent",
    "ForumEvent",
    "ForumThreadEvent",
    "ForumThreadCreateEvent",
    "ForumThreadUpdateEvent",
    "ForumThreadDeleteEvent",
    "ForumPostEvent",
    "ForumPostCreateEvent",
    "ForumPostDeleteEvent",
    "ForumReplyEvent",
    "ForumReplyCreateEvent",
    "ForumReplyDeleteEvent",
    "ForumPublishAuditResult",
    "OpenForumEvent",
    "OpenForumThreadCreateEvent",
    "OpenForumThreadUpdateEvent",
    "OpenForumThreadDeleteEvent",
    "OpenForumPostCreateEvent",
    "OpenForumPostDeleteEvent",
    "OpenForumReplyCreateEvent",
    "OpenForumReplyDeleteEvent",
    "FriendRobotEvent",
    "FriendAddEvent",
    "FriendDelEvent",
    "C2CMsgRejectEvent",
    "C2CMsgReceiveEvent",
    "GroupRobotEvent",
    "GroupAddRobotEvent",
    "GroupDelRobotEvent",
    "GroupMsgRejectEvent",
    "GroupMsgReceiveEvent",
]
