from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import parse_obj_as
from nonebot.drivers import Request

from .model import *
from .request import _request, _exclude_none

if TYPE_CHECKING:
    from nonebot.adapters.qqguild.bot import Bot
    from nonebot.adapters.qqguild.adapter import Adapter


async def _get_guild(adapter: "Adapter", bot: "Bot", guild_id: int) -> Guild:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(Guild, await _request(adapter, bot, request))


async def _me(adapter: "Adapter", bot: "Bot") -> User:
    request = Request(
        "GET",
        adapter.get_api_base() / f"users/@me",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(User, await _request(adapter, bot, request))


async def _guilds(
    adapter: "Adapter",
    bot: "Bot",
    before: Optional[str] = ...,
    after: Optional[str] = ...,
    limit: Optional[float] = ...,
) -> List[Guild]:
    request = Request(
        "GET",
        adapter.get_api_base() / f"users/@me/guilds",
        params=_exclude_none({"before": before, "after": after, "limit": limit}),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(List[Guild], await _request(adapter, bot, request))


async def _get_channels(adapter: "Adapter", bot: "Bot", guild_id: int) -> List[Channel]:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}/channels",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(List[Channel], await _request(adapter, bot, request))


async def _post_channels(
    adapter: "Adapter", bot: "Bot", guild_id: int, **data
) -> List[Channel]:
    request = Request(
        "POST",
        adapter.get_api_base() / f"guilds/{guild_id}/channels",
        json=ChannelCreate(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(List[Channel], await _request(adapter, bot, request))


async def _get_channel(adapter: "Adapter", bot: "Bot", channel_id: int) -> Channel:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _patch_channel(
    adapter: "Adapter", bot: "Bot", channel_id: int, **data
) -> Channel:
    request = Request(
        "PATCH",
        adapter.get_api_base() / f"channels/{channel_id}",
        json=ChannelUpdate(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _delete_channel(adapter: "Adapter", bot: "Bot", channel_id: int) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"channels/{channel_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _get_members(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: int,
    after: Optional[str] = ...,
    limit: Optional[float] = ...,
) -> List[Member]:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}/members",
        params=_exclude_none({"after": after, "limit": limit}),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(List[Member], await _request(adapter, bot, request))


async def _get_member(
    adapter: "Adapter", bot: "Bot", guild_id: int, user_id: int
) -> Member:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}/members/{user_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(Member, await _request(adapter, bot, request))


async def _delete_member(
    adapter: "Adapter", bot: "Bot", guild_id: int, user_id: int, **data
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"guilds/{guild_id}/members/{user_id}",
        json=DeleteMemberBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _get_guild_roles(
    adapter: "Adapter", bot: "Bot", guild_id: int
) -> GetGuildRolesReturn:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}/roles",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(GetGuildRolesReturn, await _request(adapter, bot, request))


async def _post_guild_role(
    adapter: "Adapter", bot: "Bot", guild_id: int, **data
) -> PostGuildRoleReturn:
    request = Request(
        "POST",
        adapter.get_api_base() / f"guilds/{guild_id}/roles",
        json=PostGuildRoleBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(PostGuildRoleReturn, await _request(adapter, bot, request))


async def _patch_guild_role(
    adapter: "Adapter", bot: "Bot", guild_id: int, role_id: int, **data
) -> PatchGuildRoleReturn:
    request = Request(
        "PATCH",
        adapter.get_api_base() / f"guilds/{guild_id}/roles/{role_id}",
        json=PatchGuildRoleBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(PatchGuildRoleReturn, await _request(adapter, bot, request))


async def _delete_guild_role(
    adapter: "Adapter", bot: "Bot", guild_id: int, role_id: int
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"guilds/{guild_id}/roles/{role_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _put_guild_member_role(
    adapter: "Adapter", bot: "Bot", guild_id: int, role_id: int, user_id: int, **data
) -> None:
    request = Request(
        "PUT",
        adapter.get_api_base() / f"guilds/{guild_id}/members/{user_id}/roles/{role_id}",
        json=PutGuildMemberRoleBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _delete_guild_member_role(
    adapter: "Adapter", bot: "Bot", guild_id: int, role_id: int, user_id: int, **data
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"guilds/{guild_id}/members/{user_id}/roles/{role_id}",
        json=DeleteGuildMemberRoleBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _get_channel_permissions(
    adapter: "Adapter", bot: "Bot", channel_id: int, user_id: int
) -> ChannelPermissions:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}/members/{user_id}/permissions",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(ChannelPermissions, await _request(adapter, bot, request))


async def _put_channel_permissions(
    adapter: "Adapter", bot: "Bot", channel_id: int, user_id: int, **data
) -> None:
    request = Request(
        "PUT",
        adapter.get_api_base() / f"channels/{channel_id}/members/{user_id}/permissions",
        json=PutChannelPermissionsBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _get_channel_roles_permissions(
    adapter: "Adapter", bot: "Bot", channel_id: int, role_id: int
) -> ChannelPermissions:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}/roles/{role_id}/permissions",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(ChannelPermissions, await _request(adapter, bot, request))


async def _put_channel_roles_permissions(
    adapter: "Adapter", bot: "Bot", channel_id: int, role_id: int, **data
) -> None:
    request = Request(
        "PUT",
        adapter.get_api_base() / f"channels/{channel_id}/roles/{role_id}/permissions",
        json=PutChannelRolesPermissionsBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _get_message_of_id(
    adapter: "Adapter", bot: "Bot", channel_id: int, message_id: str
) -> Message:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}/messages/{message_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(Message, await _request(adapter, bot, request))


async def _post_messages(
    adapter: "Adapter", bot: "Bot", channel_id: int, **data
) -> Message:
    request = Request(
        "POST",
        adapter.get_api_base() / f"channels/{channel_id}/messages",
        json=MessageSend(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(Message, await _request(adapter, bot, request))


async def _post_dms(adapter: "Adapter", bot: "Bot", **data) -> List[DMS]:
    request = Request(
        "POST",
        adapter.get_api_base() / f"users/@me/dms",
        json=PostDmsBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(List[DMS], await _request(adapter, bot, request))


async def _post_dms_messages(
    adapter: "Adapter", bot: "Bot", guild_id: int, **data
) -> List[Message]:
    request = Request(
        "POST",
        adapter.get_api_base() / f"dms/{guild_id}/messages",
        json=MessageSend(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(List[Message], await _request(adapter, bot, request))


async def _patch_guild_mute(
    adapter: "Adapter", bot: "Bot", guild_id: int, **data
) -> None:
    request = Request(
        "PATCH",
        adapter.get_api_base() / f"guilds/{guild_id}/mute",
        json=PatchGuildMuteBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _patch_guild_member_mute(
    adapter: "Adapter", bot: "Bot", guild_id: int, user_id: int, **data
) -> None:
    request = Request(
        "PATCH",
        adapter.get_api_base() / f"guilds/{guild_id}/members/{user_id}/mute",
        json=PatchGuildMemberMuteBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _post_guild_announces(
    adapter: "Adapter", bot: "Bot", guild_id: int, **data
) -> None:
    request = Request(
        "POST",
        adapter.get_api_base() / f"guilds/{guild_id}/announces",
        json=PostGuildAnnouncesBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _delete_guild_announces(
    adapter: "Adapter", bot: "Bot", guild_id: int, message_id: str
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"guilds/{guild_id}/announces/{message_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _post_channel_announces(
    adapter: "Adapter", bot: "Bot", channel_id: int, **data
) -> Announces:
    request = Request(
        "POST",
        adapter.get_api_base() / f"channels/{channel_id}/announces",
        json=PostChannelAnnouncesBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(Announces, await _request(adapter, bot, request))


async def _delete_channel_announces(
    adapter: "Adapter", bot: "Bot", channel_id: int, message_id: str
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"channels/{channel_id}/announces/{message_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _get_schedules(
    adapter: "Adapter", bot: "Bot", channel_id: int, **data
) -> List[Schedule]:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}/schedules",
        json=GetSchedulesBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(List[Schedule], await _request(adapter, bot, request))


async def _post_schedule(
    adapter: "Adapter", bot: "Bot", channel_id: int, **data
) -> Schedule:
    request = Request(
        "POST",
        adapter.get_api_base() / f"channels/{channel_id}/schedules",
        json=ScheduleCreate(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(Schedule, await _request(adapter, bot, request))


async def _get_schedule(
    adapter: "Adapter", bot: "Bot", channel_id: int, schedule_id: int
) -> Schedule:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}/schedules/{schedule_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(Schedule, await _request(adapter, bot, request))


async def _patch_schedule(
    adapter: "Adapter", bot: "Bot", channel_id: int, schedule_id: int, **data
) -> Schedule:
    request = Request(
        "PATCH",
        adapter.get_api_base() / f"channels/{channel_id}/schedules/{schedule_id}",
        json=ScheduleUpdate(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(Schedule, await _request(adapter, bot, request))


async def _delete_schedule(
    adapter: "Adapter", bot: "Bot", channel_id: int, schedule_id: int
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"channels/{channel_id}/schedules/{schedule_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _audio_control(
    adapter: "Adapter", bot: "Bot", channel_id: int, **data
) -> None:
    request = Request(
        "POST",
        adapter.get_api_base() / f"channels/{channel_id}/audio",
        json=AudioControl(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _get_guild_api_permission(
    adapter: "Adapter", bot: "Bot", guild_id: int
) -> List[APIPermission]:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}/api_permission",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(List[APIPermission], await _request(adapter, bot, request))


async def _post_api_permission_demand(
    adapter: "Adapter", bot: "Bot", guild_id: int, **data
) -> List[APIPermissionDemand]:
    request = Request(
        "POST",
        adapter.get_api_base() / f"guilds/{guild_id}/api_permission/demand",
        json=PostApiPermissionDemandBody(**data).dict(exclude_none=True),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(
        List[APIPermissionDemand], await _request(adapter, bot, request)
    )


async def _url_get(adapter: "Adapter", bot: "Bot") -> UrlGetReturn:
    request = Request(
        "GET",
        adapter.get_api_base() / f"gateway",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(UrlGetReturn, await _request(adapter, bot, request))


async def _shard_url_get(adapter: "Adapter", bot: "Bot") -> ShardUrlGetReturn:
    request = Request(
        "GET",
        adapter.get_api_base() / f"gateway/bot",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(ShardUrlGetReturn, await _request(adapter, bot, request))


async def _put_message_reaction(
    adapter: "Adapter", bot: "Bot", channel_id: int, message_id: str, type: int, id: str
) -> None:
    request = Request(
        "PUT",
        adapter.get_api_base()
        / f"channels/{channel_id}/messages/{message_id}/reactions/{type}/{id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _delete_own_message_reaction(
    adapter: "Adapter", bot: "Bot", channel_id: int, message_id: str, type: int, id: str
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base()
        / f"channels/{channel_id}/messages/{message_id}/reactions/{type}/{id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _put_pins_message(
    adapter: "Adapter", bot: "Bot", channel_id: int, message_id: str
) -> None:
    request = Request(
        "PUT",
        adapter.get_api_base() / f"channels/{channel_id}/pins/{message_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _delete_pins_message(
    adapter: "Adapter", bot: "Bot", channel_id: int, message_id: str
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"channels/{channel_id}/pins/{message_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _get_pins_message(
    adapter: "Adapter", bot: "Bot", channel_id: int
) -> PinsMessage:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}/pins",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_obj_as(PinsMessage, await _request(adapter, bot, request))


API_HANDLERS = {
    "get_guild": _get_guild,
    "me": _me,
    "guilds": _guilds,
    "get_channels": _get_channels,
    "post_channels": _post_channels,
    "get_channel": _get_channel,
    "patch_channel": _patch_channel,
    "delete_channel": _delete_channel,
    "get_members": _get_members,
    "get_member": _get_member,
    "delete_member": _delete_member,
    "get_guild_roles": _get_guild_roles,
    "post_guild_role": _post_guild_role,
    "patch_guild_role": _patch_guild_role,
    "delete_guild_role": _delete_guild_role,
    "put_guild_member_role": _put_guild_member_role,
    "delete_guild_member_role": _delete_guild_member_role,
    "get_channel_permissions": _get_channel_permissions,
    "put_channel_permissions": _put_channel_permissions,
    "get_channel_roles_permissions": _get_channel_roles_permissions,
    "put_channel_roles_permissions": _put_channel_roles_permissions,
    "get_message_of_id": _get_message_of_id,
    "post_messages": _post_messages,
    "post_dms": _post_dms,
    "post_dms_messages": _post_dms_messages,
    "patch_guild_mute": _patch_guild_mute,
    "patch_guild_member_mute": _patch_guild_member_mute,
    "post_guild_announces": _post_guild_announces,
    "delete_guild_announces": _delete_guild_announces,
    "post_channel_announces": _post_channel_announces,
    "delete_channel_announces": _delete_channel_announces,
    "get_schedules": _get_schedules,
    "post_schedule": _post_schedule,
    "get_schedule": _get_schedule,
    "patch_schedule": _patch_schedule,
    "delete_schedule": _delete_schedule,
    "audio_control": _audio_control,
    "get_guild_api_permission": _get_guild_api_permission,
    "post_api_permission_demand": _post_api_permission_demand,
    "url_get": _url_get,
    "shard_url_get": _shard_url_get,
    "put_message_reaction": _put_message_reaction,
    "delete_own_message_reaction": _delete_own_message_reaction,
    "put_pins_message": _put_pins_message,
    "delete_pins_message": _delete_pins_message,
    "get_pins_message": _get_pins_message,
}
