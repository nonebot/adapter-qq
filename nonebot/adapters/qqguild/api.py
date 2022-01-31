from typing import TYPE_CHECKING, Any, Dict, List, Union, Callable, Optional

from pydantic import parse_raw_as
from nonebot.drivers import Request

from .model import (
    User,
    Guild,
    Channel,
    Gateway,
    GuildRoles,
    ChannelType,
    PrivateType,
    ChannelSubType,
    SpeakPermission,
    GatewayWithShards,
)

if TYPE_CHECKING:
    from .bot import Bot
    from .adapter import Adapter


async def _request(adapter: "Adapter", bot: "Bot", request: Request) -> Any:
    data = await adapter.request(request)
    assert data.content is not None
    return data.content


async def _get_me(adapter: "Adapter", bot: "Bot") -> User:
    request = Request(
        "GET",
        adapter.get_api_base() / "/users/@me",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return User.parse_raw(await _request(adapter, bot, request))


async def _get_me_guilds(adapter: "Adapter", bot: "Bot") -> List[Guild]:
    request = Request(
        "GET",
        adapter.get_api_base() / "users/@me/guilds",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(List[Guild], await _request(adapter, bot, request))


async def _get_guild(adapter: "Adapter", bot: "Bot", *, guild_id: str) -> Guild:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return Guild.parse_raw(await _request(adapter, bot, request))


async def _get_channels(
    adapter: "Adapter", bot: "Bot", *, guild_id: str
) -> List[Channel]:
    request = Request(
        "GET",
        adapter.get_api_base() / f"/guilds/{guild_id}/channels",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(List[Channel], await _request(adapter, bot, request))


async def _get_channel(adapter: "Adapter", bot: "Bot", *, channel_id: str) -> Channel:
    request = Request(
        "GET",
        adapter.get_api_base() / f"channels/{channel_id}",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(Channel, await _request(adapter, bot, request))


async def _create_channel(
    adapter: "Adapter",
    bot: "Bot",
    *,
    guild_id: str,
    name: str,
    type: Union[ChannelType, int],
    sub_type: Union[ChannelSubType, int],
    position: Optional[int] = None,
    parent_id: Optional[str] = None,
    private_type: Union[PrivateType, int] = PrivateType.PUBLIC,
    private_user_ids: Optional[List[str]] = None,
    speak_permission: Union[SpeakPermission, int] = SpeakPermission.PUBLIC,
    application_id: Optional[str] = None,
) -> Channel:
    # TODO
    request = Request(
        "POST",
        adapter.get_api_base() / f"guilds/{guild_id}/channels",
        json={},
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return parse_raw_as(Channel, await _request(adapter, bot, request))


async def _get_guild_roles(adapter: "Adapter", bot: "Bot", guild_id: str) -> GuildRoles:
    request = Request(
        "GET",
        adapter.get_api_base() / f"guilds/{guild_id}/roles",
        headers={"Authorization": adapter.get_authorization(bot.bot_info)},
    )
    return GuildRoles.parse_raw(await _request(adapter, bot, request))


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


api_handlers: Dict[str, Callable[..., Any]] = {
    # User API
    "get_me": _get_me,
    "get_me_guilds": _get_me_guilds,
    # Guild API
    "get_guild": _get_guild,
    # Channel API
    "get_channels": _get_channels,
    # Guild Role API
    "get_guild_roles": _get_guild_roles,
    # WebSocket API
    "get_gateway": _get_gateway,
    "get_gateway_with_shards": _get_gateway_with_shards,
}
