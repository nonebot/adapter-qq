import json
from typing import TYPE_CHECKING, Any, Dict, List, Union, Callable, Optional

from pydantic import parse_raw_as
from nonebot.drivers import Request

from .model import (
    User,
    Guild,
    Member,
    Channel,
    Gateway,
    CreateRole,
    GuildRoles,
    UpdateRole,
    RoleCreateInfo,
    GatewayWithShards,
    _ChannelType,
)

if TYPE_CHECKING:
    from .bot import Bot
    from .adapter import Adapter


async def _request(adapter: "Adapter", bot: "Bot", request: Request) -> Any:
    data = await adapter.request(request)
    assert data.content is not None
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
        content=json.dumps(data),
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(_ChannelType, await _request(adapter, bot, request))


async def _update_channel(
    adapter: "Adapter", bot: "Bot", *, channel_id: str, **data
) -> Channel:
    request = Request(
        "PATCH",
        adapter.get_api_base() / f"channels/{channel_id}",
        content=json.dumps(data),
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
        content=json.dumps({"add_blacklist": add_blacklist}),
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
        content=json.dumps(data.dict(exclude_none=True)),
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
        content=json.dumps(data.dict(exclude_none=True)),
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
        content=json.dumps(data),
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
        content=json.dumps(data),
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
    # WebSocket API
    "get_gateway": _get_gateway,
    "get_gateway_with_shards": _get_gateway_with_shards,
}
