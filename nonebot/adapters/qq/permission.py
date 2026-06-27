from nonebot.permission import Permission

from .event import AtMessageCreateEvent, MessageCreateEvent, GroupAtMessageCreateEvent, GroupMessageCreateEvent


async def _guild_channel_admin(
    event: AtMessageCreateEvent | MessageCreateEvent,
) -> bool:
    return "5" in getattr(event.member, "roles", ())


async def _guild_admin(event: AtMessageCreateEvent | MessageCreateEvent) -> bool:
    return "2" in getattr(event.member, "roles", ())


async def _guild_owner(event: AtMessageCreateEvent | MessageCreateEvent) -> bool:
    return "4" in getattr(event.member, "roles", ())


GUILD_CHANNEL_ADMIN: Permission = Permission(_guild_channel_admin)
"""匹配任意子频道管理员聊消息类型事件"""
GUILD_ADMIN: Permission = Permission(_guild_admin)
"""匹配任意频道管理员聊消息类型事件"""
GUILD_OWNER: Permission = Permission(_guild_owner)
"""匹配任意频道群主群消息类型事件"""


async def _group_member(event: GroupAtMessageCreateEvent | GroupMessageCreateEvent) -> bool:
    return event.author.member_role == "member"


async def _group_admin(event: GroupAtMessageCreateEvent | GroupMessageCreateEvent) -> bool:
    return event.author.member_role == "admin"


async def _group_owner(event: GroupAtMessageCreateEvent | GroupMessageCreateEvent) -> bool:
    return event.author.member_role == "owner"


GROUP_MEMBER: Permission = Permission(_group_member)
"""匹配任意群员群聊消息类型事件"""
GROUP_ADMIN: Permission = Permission(_group_admin)
"""匹配任意群管理员群聊消息类型事件"""
GROUP_OWNER: Permission = Permission(_group_owner)
"""匹配任意群主群聊消息类型事件"""

__all__ = [
    "GUILD_ADMIN",
    "GUILD_CHANNEL_ADMIN",
    "GUILD_OWNER",
    "GROUP_ADMIN",
    "GROUP_MEMBER",
    "GROUP_OWNER",
]
