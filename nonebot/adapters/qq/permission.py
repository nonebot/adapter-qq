from typing import Union

from nonebot.permission import Permission

from .event import MessageCreateEvent, AtMessageCreateEvent


async def _guild_channel_admin(
    event: Union[AtMessageCreateEvent, MessageCreateEvent]
) -> bool:
    return "5" in getattr(event.member, "roles", ())


async def _guild_admin(event: Union[AtMessageCreateEvent, MessageCreateEvent]) -> bool:
    return "2" in getattr(event.member, "roles", ())


async def _guild_owner(event: Union[AtMessageCreateEvent, MessageCreateEvent]) -> bool:
    return "4" in getattr(event.member, "roles", ())


GUILD_CHANNEL_ADMIN: Permission = Permission(_guild_channel_admin)
"""匹配任意子频道管理员聊消息类型事件"""
GUILD_ADMIN: Permission = Permission(_guild_admin)
"""匹配任意频道管理员聊消息类型事件"""
GUILD_OWNER: Permission = Permission(_guild_owner)
"""匹配任意频道群主群消息类型事件"""

__all__ = [
    "GUILD_CHANNEL_ADMIN",
    "GUILD_ADMIN",
    "GUILD_OWNER",
]
