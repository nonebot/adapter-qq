from typing import Union

from nonebot.permission import Permission

from .event import MessageCreateEvent, AtMessageCreateEvent


async def _guild_admin(event: Union[AtMessageCreateEvent, MessageCreateEvent]) -> bool:
    return 2 in event.member.roles


async def _guild_owner(event: Union[AtMessageCreateEvent, MessageCreateEvent]) -> bool:
    return 4 in event.member.roles


GUILD_ADMIN: Permission = Permission(_guild_admin)
"""匹配任意频道管理员群聊消息类型事件"""
GUILD_OWNER: Permission = Permission(_guild_owner)
"""匹配任意频道群主群聊消息类型事件"""

__all__ = [
    "GUILD_ADMIN",
    "GUILD_OWNER",
]
