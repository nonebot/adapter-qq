from typing import TYPE_CHECKING, Any, Dict, List, Callable, Optional

from pydantic import parse_raw_as
from nonebot.drivers import Request
from pydantic.json import pydantic_encoder

from .model import (
    DMS,
    User,
    Guild,
    Member,
    Channel,
    Gateway,
    Message,
    Announce,
    Schedule,
    CreateRole,
    GuildRoles,
    UpdateRole,
    AvailableAPIs,
    RoleCreateInfo,
    GatewayWithShards,
    APIPermissionDemand,
    ChannelRolePermissions,
    ChannelUserPermissions,
    _ChannelType,
)

if TYPE_CHECKING:
    from .bot import Bot
    from .adapter import Adapter


async def _request(adapter: "Adapter", bot: "Bot", request: Request) -> Any:
    data = await adapter.request(request)
    assert 200 <= data.status_code < 300
    return data.content


# User API
async def _get_me(adapter: "Adapter", bot: "Bot") -> User:
    request = Request(
        "GET",
        adapter.get_api_base() / "/users/@me",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return User.parse_raw(await _request(adapter, bot, request))


async def _get_me_guilds(adapter: "Adapter", bot: "Bot", **data) -> List[Guild]:
    request = Request(
        "GET",
        adapter.get_api_base() / "users/@me/guilds",
        params=data,
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(List[Guild], await _request(adapter, bot, request))


# Guild API
async def _get_guild(adapter: "Adapter", bot: "Bot", *, guild_id: str) -> Guild:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return Guild.parse_raw(await _request(adapter, bot, request))


# Channel API
async def _get_channels(
    adapter: "Adapter", bot: "Bot", *, guild_id: str
) -> List[_ChannelType]:
    request = Request(
        "GET",
        adapter.get_api_base() / f"/guilds/{guild_id}/channels",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(List[_ChannelType], await _request(adapter, bot, request))


async def _get_channel(adapter: "Adapter", bot: "Bot", *, channel_id: str) -> Channel:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(_ChannelType, await _request(adapter, bot, request))


async def _create_channel(
    adapter: "Adapter", bot: "Bot", *, guild_id: str, **data
) -> Channel:
    request = Request(
        "POST",
        adapter.get_api_base() / f"guilds/{guild_id}/channels",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(_ChannelType, await _request(adapter, bot, request))


async def _update_channel(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, **data
) -> Channel:
    request = Request(
        "PATCH",
        adapter.get_api_base() / f"channels/{channel_id}",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(_ChannelType, await _request(adapter, bot, request))


async def _delete_channel(
    adapter: "Adapter",
    bot: "Bot",
    *,
    channel_id: str,
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"channels/{channel_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


# Member API
async def _get_guild_members(
    adapter: "Adapter", bot: "Bot", *, guild_id: str, **data
) -> List[Member]:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}/members",
        params=data,
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(List[Member], await _request(adapter, bot, request))


async def _get_guild_member(
    adapter: "Adapter", bot: "Bot", *, guild_id: str, user_id: str
) -> Member:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}/members/{user_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return Member.parse_raw(await _request(adapter, bot, request))


async def _delete_guild_member(
    adapter: "Adapter",
    bot: "Bot",
    *,
    guild_id: str,
    user_id: str,
    add_blacklist: bool = False,
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"guilds/{guild_id}/members/{user_id}",
        content=pydantic_encoder({"add_blacklist": add_blacklist}),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


# Guild Role API
async def _get_guild_roles(
    adapter: "Adapter", bot: "Bot", *, guild_id: str
) -> GuildRoles:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}/roles",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return GuildRoles.parse_raw(await _request(adapter, bot, request))


async def _create_guild_role(
    adapter: "Adapter", bot: "Bot", *, guild_id: str, **data
) -> CreateRole:
    data = RoleCreateInfo(**data)
    request = Request(
        "POST",
        adapter.get_api_base() / f"guilds/{guild_id}/roles",
        content=pydantic_encoder(data.dict(exclude_none=True)),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return CreateRole.parse_raw(await _request(adapter, bot, request))


async def _update_guild_role(
    adapter: "Adapter", bot: "Bot", *, guild_id: str, role_id: str, **data
) -> UpdateRole:
    data = RoleCreateInfo(**data)
    request = Request(
        "PATCH",
        adapter.get_api_base() / f"guilds/{guild_id}/roles/{role_id}",
        content=pydantic_encoder(data.dict(exclude_none=True)),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return UpdateRole.parse_raw(await _request(adapter, bot, request))


async def _delete_guild_role(
    adapter: "Adapter", bot: "Bot", *, guild_id: str, role_id: str
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"guilds/{guild_id}/roles/{role_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _create_guild_role_member(
    adapter: "Adapter",
    bot: "Bot",
    *,
    guild_id: str,
    user_id: str,
    role_id: str,
    channel_id: Optional[str] = None,
) -> None:
    data = {}
    if channel_id is not None:
        data["channel"] = {"id": channel_id}
    request = Request(
        "PUT",
        adapter.get_api_base() / f"guilds/{guild_id}/members/{user_id}/roles/{role_id}",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _delete_guild_role_member(
    adapter: "Adapter",
    bot: "Bot",
    *,
    guild_id: str,
    user_id: str,
    role_id: str,
    channel_id: Optional[str] = None,
) -> None:
    data = {}
    if channel_id is not None:
        data["channel"] = {"id": channel_id}
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"guilds/{guild_id}/members/{user_id}/roles/{role_id}",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


# Channel Permission API
async def _get_channel_permissions(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, user_id: str
) -> ChannelUserPermissions:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}/members/{user_id}/permissions",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return ChannelUserPermissions.parse_raw(await _request(adapter, bot, request))


async def _update_channel_permissions(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, user_id: str, **data
) -> None:
    request = Request(
        "PUT",
        adapter.get_api_base() / f"channels/{channel_id}/members/{user_id}/permissions",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _get_channel_role_permissions(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, role_id: str
) -> ChannelRolePermissions:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}/roles/{role_id}/permissions",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return ChannelRolePermissions.parse_raw(await _request(adapter, bot, request))


async def _update_channel_role_permissions(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, role_id: str, **data
) -> None:
    request = Request(
        "PUT",
        adapter.get_api_base() / f"channels/{channel_id}/roles/{role_id}/permissions",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


# Message API
async def _get_message(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, message_id: str
) -> Message:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}/messages/{message_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return Message.parse_raw(await _request(adapter, bot, request))


async def _get_messages(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, **data
) -> List[Message]:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}/messages",
        params=data,
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(List[Message], await _request(adapter, bot, request))


async def _post_message(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, **data
) -> Message:
    request = Request(
        "POST",
        adapter.get_api_base() / f"channels/{channel_id}/messages",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return Message.parse_raw(await _request(adapter, bot, request))


async def _recall_message(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, message_id: str
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"channels/{channel_id}/messages/{message_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


# DMS API
async def _create_direct_message(adapter: "Adapter", bot: "Bot", **data) -> DMS:
    request = Request(
        "POST",
        adapter.get_api_base() / f"users/@me/dms",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return DMS.parse_raw(await _request(adapter, bot, request))


async def _post_direct_message(
    adapter: "Adapter", bot: "Bot", *, guild_id: str, **data
) -> Message:
    request = Request(
        "POST",
        adapter.get_api_base() / f"dms/{guild_id}/messages",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return Message.parse_raw(await _request(adapter, bot, request))


# Mute API
async def _mute_all(adapter: "Adapter", bot: "Bot", *, guild_id: str, **data) -> None:
    request = Request(
        "PATCH",
        adapter.get_api_base() / f"guilds/{guild_id}/mute",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _mute_member(
    adapter: "Adapter", bot: "Bot", *, guild_id: str, user_id: str, **data
) -> None:
    request = Request(
        "PATCH",
        adapter.get_api_base() / f"guilds/{guild_id}/members/{user_id}/mute",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


# Announces API
async def _create_announce(
    adapter: "Adapter", bot: "Bot", *, guild_id: str, **data
) -> Announce:
    request = Request(
        "POST",
        adapter.get_api_base() / f"guilds/{guild_id}/announces",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return Announce.parse_raw(await _request(adapter, bot, request))


async def _delete_announce(
    adapter: "Adapter", bot: "Bot", *, guild_id: str, message_id: str
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"guilds/{guild_id}/announces/{message_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


async def _create_channel_announce(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, **data
) -> Announce:
    request = Request(
        "POST",
        adapter.get_api_base() / f"channels/{channel_id}/announces",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return Announce.parse_raw(await _request(adapter, bot, request))


async def _delete_channel_announce(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, message_id: str
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"channels/{channel_id}/announces/{message_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


# Schedule API
async def _get_channel_schedules(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, **data
) -> List[Schedule]:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}/schedules",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(List[Schedule], await _request(adapter, bot, request))


async def _get_channel_schedule(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, schedule_id: str
) -> Schedule:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}/schedules/{schedule_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return Schedule.parse_raw(await _request(adapter, bot, request))


async def _create_channel_schedule(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, **data
) -> Schedule:
    request = Request(
        "POST",
        adapter.get_api_base() / f"channels/{channel_id}/schedules",
        content=pydantic_encoder({"schedule": data}),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return Schedule.parse_raw(await _request(adapter, bot, request))


async def _update_channel_schedule(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, schedule_id: str, **data
) -> Schedule:
    request = Request(
        "PATCH",
        adapter.get_api_base() / f"channels/{channel_id}/schedules/{schedule_id}",
        content=pydantic_encoder({"schedule": data}),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return Schedule.parse_raw(await _request(adapter, bot, request))


async def _delete_channel_schedule(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, schedule_id: str
) -> None:
    request = Request(
        "DELETE",
        adapter.get_api_base() / f"channels/{channel_id}/schedules/{schedule_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


# Audio API
async def _control_audio(
    adapter: "Adapter", bot: "Bot", channel_id: str, **data
) -> None:
    request = Request(
        "POST",
        adapter.get_api_base() / f"channels/{channel_id}/audio",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


# Permission API
async def _get_permissions(
    adapter: "Adapter", bot: "Bot", *, guild_id: str
) -> AvailableAPIs:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}/api_permission",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return AvailableAPIs.parse_raw(await _request(adapter, bot, request))


async def _post_permission_demand(
    adapter: "Adapter", bot: "Bot", *, guild_id: str, **data
) -> APIPermissionDemand:
    request = Request(
        "POST",
        adapter.get_api_base() / f"guilds/{guild_id}/api_permission/demand",
        content=pydantic_encoder(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return await _request(adapter, bot, request)


# WebSocket API
async def _get_gateway(adapter: "Adapter", bot: "Bot") -> Gateway:
    request = Request(
        "GET",
        adapter.get_api_base() / "gateway",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return Gateway.parse_raw(await _request(adapter, bot, request))


async def _get_gateway_with_shards(adapter: "Adapter", bot: "Bot") -> GatewayWithShards:
    request = Request(
        "GET",
        adapter.get_api_base() / "gateway" / "bot",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return GatewayWithShards.parse_raw(await _request(adapter, bot, request))


API_HANDLERS: Dict[str, Callable[..., Any]] = {
    # User API
    "get_me": _get_me,
    "get_me_guilds": _get_me_guilds,
    # Guild API
    "get_guild": _get_guild,
    # Channel API
    "get_channels": _get_channels,
    "get_channel": _get_channel,
    "create_channel": _create_channel,
    "update_channel": _update_channel,
    "delete_channel": _delete_channel,
    # Member API
    "get_guild_members": _get_guild_members,
    "get_guild_member": _get_guild_member,
    "delete_guild_member": _delete_guild_member,
    # Guild Role API
    "get_guild_roles": _get_guild_roles,
    "create_guild_role": _create_guild_role,
    "update_guild_role": _update_guild_role,
    "delete_guild_role": _delete_guild_role,
    "create_guild_role_member": _create_guild_role_member,
    "delete_guild_role_member": _delete_guild_role_member,
    # Channel Permission API
    "get_channel_permissions": _get_channel_permissions,
    "update_channel_permissions": _update_channel_permissions,
    "get_channel_role_permissions": _get_channel_role_permissions,
    "update_channel_role_permissions": _update_channel_role_permissions,
    # Message API
    "get_message": _get_message,
    "get_messages": _get_messages,
    "post_message": _post_message,
    "recall_message": _recall_message,
    # DMS API
    "create_direct_message": _create_direct_message,
    "post_direct_message": _post_direct_message,
    # Mute API
    "mute_all": _mute_all,
    "mute_member": _mute_member,
    # Announces API
    "create_announce": _create_announce,
    "delete_announce": _delete_announce,
    "create_channel_announce": _create_channel_announce,
    "delete_channel_announce": _delete_channel_announce,
    # Schedule API
    "get_channel_schedules": _get_channel_schedules,
    "get_channel_schedule": _get_channel_schedule,
    "create_channel_schedule": _create_channel_schedule,
    "update_channel_schedule": _update_channel_schedule,
    "delete_channel_schedule": _delete_channel_schedule,
    # Audio API
    "control_audio": _control_audio,
    # API Permission API
    "get_permissions": _get_permissions,
    "post_permission_demand": _post_permission_demand,
    # WebSocket API
    "get_gateway": _get_gateway,
    "get_gateway_with_shards": _get_gateway_with_shards,
}
