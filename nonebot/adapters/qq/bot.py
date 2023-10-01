import json
from typing_extensions import Never, override
from datetime import datetime, timezone, timedelta
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Union,
    Literal,
    NoReturn,
    Optional,
    cast,
    overload,
)

from nonebot.message import handle_event
from pydantic import BaseModel, parse_obj_as
from nonebot.drivers import Request, Response

from nonebot.adapters import Bot as BaseBot

from .config import BotInfo
from .utils import API, log, exclude_none
from .models import Message as GuildMessage
from .message import Message, MessageSegment
from .models import DMS, User, Guild, Member, Channel
from .event import Event, ReadyEvent, MessageEvent, DirectMessageCreateEvent
from .exception import (
    ActionFailed,
    NetworkError,
    AuditException,
    ApiNotAvailable,
    RateLimitException,
    UnauthorizedException,
)
from .models import (
    Dispatch,
    RichText,
    Schedule,
    EmojiType,
    MessageArk,
    RemindType,
    AudioStatus,
    ChannelType,
    PinsMessage,
    PrivateType,
    AudioControl,
    MessageEmbed,
    UrlGetReturn,
    ChannelSubType,
    MessageSetting,
    GetThreadReturn,
    MessageKeyboard,
    MessageMarkdown,
    PutThreadReturn,
    SpeakPermission,
    MessageReference,
    RecommendChannel,
    ShardUrlGetReturn,
    ChannelPermissions,
    APIPermissionDemand,
    GetGuildRolesReturn,
    PostGuildRoleReturn,
    GetRoleMembersReturn,
    GetThreadsListReturn,
    PatchGuildRoleReturn,
    GetReactionUsersReturn,
    APIPermissionDemandIdentify,
    GetGuildAPIPermissionReturn,
)

if TYPE_CHECKING:
    from .adapter import Adapter


async def _check_reply(bot: "Bot", event: MessageEvent) -> None:
    """检查消息中存在的回复，赋值 `event.reply`, `event.to_me`。

    参数:
        bot: Bot 对象
        event: MessageEvent 对象
    """
    if event.message_reference is None:
        return
    try:
        event.reply = await bot.get_message_of_id(
            channel_id=event.channel_id,  # type: ignore
            message_id=event.message_reference.message_id,  # type: ignore
        )
        if event.reply.message.author.id == bot.self_info.id:  # type: ignore
            event.to_me = True
    except Exception as e:
        log("WARNING", f"Error when getting message reply info: {repr(e)}", e)


def _check_at_me(bot: "Bot", event: MessageEvent):
    if event.mentions is not None and bot.self_info.id in [
        user.id for user in event.mentions
    ]:
        event.to_me = True

    def _is_at_me_seg(segment: MessageSegment) -> bool:
        return segment.type == "mention_user" and segment.data.get("user_id") == str(
            bot.self_info.id
        )

    message = event.get_message()

    # ensure message is not empty
    if not message:
        message.append(MessageSegment.text(""))

    deleted = False
    if _is_at_me_seg(message[0]):
        message.pop(0)
        deleted = True
        if message and message[0].type == "text":
            message[0].data["text"] = message[0].data["text"].lstrip("\xa0").lstrip()
            if not message[0].data["text"]:
                del message[0]

    if not deleted:
        # check the last segment
        i = -1
        last_msg_seg = message[i]
        if (
            last_msg_seg.type == "text"
            and not last_msg_seg.data["text"].strip()
            and len(message) >= 2
        ):
            i -= 1
            last_msg_seg = message[i]

        if _is_at_me_seg(last_msg_seg):
            deleted = True
            del message[i:]

    if not message:
        message.append(MessageSegment.text(""))


class Bot(BaseBot):
    adapter: "Adapter"

    @override
    def __init__(self, adapter: "Adapter", self_id: str, bot_info: BotInfo):
        super().__init__(adapter, self_id)

        # Bot 配置信息
        self.bot_info: BotInfo = bot_info

        # Bot 自身信息
        self._self_info: Optional[User] = None
        # Bot 当前 session id，可用于 Resume 重连
        self._session_id: Optional[str] = None
        # Bot 当前事件序号，可用于 Resume 重连
        self._sequence: Optional[int] = None

        # 群聊机器人鉴权信息
        self._access_token: Optional[str] = None
        self._expires_in: Optional[datetime] = None

    @override
    def __getattr__(self, name: str) -> NoReturn:
        raise AttributeError(
            f'"{self.__class__.__name__}" object has no attribute "{name}"'
        )

    @property
    def self_info(self) -> User:
        """Bot 自身信息，仅当 Bot 连接鉴权完成后可用"""
        if self._self_info is None:
            raise RuntimeError(f"Bot {self.bot_info} is not connected!")
        return self._self_info

    @property
    def ready(self) -> bool:
        """Bot 是否已经准备就绪"""
        return self._session_id is not None

    @property
    def session_id(self) -> str:
        """Bot 当前的 session id"""
        if self._session_id is None:
            raise RuntimeError(f"Bot {self.self_id} is not connected!")
        return self._session_id

    @property
    def sequence(self) -> int:
        """Bot 当前事件序列号"""
        if self._sequence is None:
            raise RuntimeError(f"Bot {self.bot_info.id} is not connected!")
        return self._sequence

    def on_ready(self, event: ReadyEvent) -> None:
        self._self_info = event.user
        self._session_id = event.session_id

    def on_dispatch(self, payload: Dispatch) -> None:
        self._sequence = payload.sequence

    def reset(self) -> None:
        """清理 Bot 连接信息"""
        self._session_id = None
        self._sequence = None

    async def get_access_token(self) -> str:
        if self._access_token is None or (
            self._expires_in
            and datetime.now(timezone.utc) > self._expires_in - timedelta(seconds=30)
        ):
            request = Request(
                "POST",
                self.adapter.get_auth_base(),
                json={
                    "appId": self.bot_info.id,
                    "clientSecret": self.bot_info.secret,
                },
            )
            resp = await self.adapter.request(request)
            if resp.status_code != 200 or not resp.content:
                raise NetworkError(
                    f"Get authorization failed with status code {resp.status_code}."
                    " Please check your config."
                )
            data = json.loads(resp.content)
            self._access_token = cast(str, data["access_token"])
            self._expires_in = datetime.now(timezone.utc) + timedelta(
                seconds=int(data["expires_in"])
            )
        return self._access_token

    async def _get_authorization_header(self) -> str:
        """获取当前 Bot 的鉴权信息"""
        if self.bot_info.is_group_bot:
            return f"QQBot {await self.get_access_token()}"
        return f"Bot {self.bot_info.id}.{self.bot_info.token}"

    async def get_authorization_header(self) -> Dict[str, str]:
        """获取当前 Bot 的鉴权信息"""
        headers = {"Authorization": await self._get_authorization_header()}
        if self.bot_info.is_group_bot:
            headers["X-Union-Appid"] = self.bot_info.id
        return headers

    async def handle_event(self, event: Event) -> None:
        if isinstance(event, MessageEvent):
            await _check_reply(self, event)
            _check_at_me(self, event)
        await handle_event(self, event)

    @staticmethod
    def _extract_send_message(
        message: Union[str, Message, MessageSegment]
    ) -> Dict[str, Any]:
        message = MessageSegment.text(message) if isinstance(message, str) else message
        message = message if isinstance(message, Message) else Message(message)

        kwargs = {}
        content = message.extract_content() or None
        kwargs["content"] = content
        if embed := (message["embed"] or None):
            kwargs["embed"] = embed[-1].data["embed"]
        if ark := (message["ark"] or None):
            kwargs["ark"] = ark[-1].data["ark"]
        if image := (message["attachment"] or None):
            kwargs["image"] = image[-1].data["url"]
        if file_image := (message["file_image"] or None):
            kwargs["file_image"] = file_image[-1].data["content"]
        if markdown := (message["markdown"] or None):
            kwargs["markdown"] = markdown[-1].data["markdown"]
        if reference := (message["reference"] or None):
            kwargs["message_reference"] = reference[-1].data["reference"]

        return kwargs

    async def send_to_dms(
        self,
        guild_id: int,
        message: Union[str, Message, MessageSegment],
        msg_id: Optional[int] = None,
    ) -> Any:
        return await self.post_dms_messages(
            guild_id=guild_id,
            msg_id=msg_id,  # type: ignore
            **self._extract_send_message(message=message),
        )

    async def send_to(
        self,
        channel_id: int,
        message: Union[str, Message, MessageSegment],
        msg_id: Optional[int] = None,
    ) -> Any:
        return await self.post_messages(
            channel_id=channel_id,
            msg_id=msg_id,  # type: ignore
            **self._extract_send_message(message=message),
        )

    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs,
    ) -> Any:
        if not isinstance(event, MessageEvent) or not event.channel_id or not event.id:
            raise RuntimeError("Event cannot be replied to!")

        if isinstance(event, DirectMessageCreateEvent):
            # 私信需要使用 post_dms_messages
            # https://bot.q.qq.com/wiki/develop/api/openapi/dms/post_dms_messages.html#%E5%8F%91%E9%80%81%E7%A7%81%E4%BF%A1
            return await self.send_to_dms(
                guild_id=event.guild_id,  # type: ignore
                message=message,
                msg_id=event.id,  # type: ignore
            )
        else:
            return await self.send_to(
                channel_id=event.channel_id,
                message=message,
                msg_id=event.id,  # type: ignore
            )

    # API request methods
    def _handle_response(self, response: Response) -> Any:
        if response.status_code == 201 or response.status_code == 202:
            if response.content and (content := json.loads(response.content)):
                audit_id = (
                    content.get("response", {})
                    .get("message_audit", {})
                    .get("audit_id", None)
                )
                if audit_id:
                    raise AuditException(audit_id)
            raise ActionFailed(response)
        elif 200 <= response.status_code < 300:
            return response.content and json.loads(response.content)
        elif response.status_code == 401:
            raise UnauthorizedException(response)
        elif response.status_code in (404, 405):
            raise ApiNotAvailable
        elif response.status_code == 429:
            raise RateLimitException(response)
        else:
            raise ActionFailed(response)

    async def _request(self, request: Request) -> Any:
        request.headers.update(await self.get_authorization_header())

        try:
            response = await self.adapter.request(request)
        except Exception as e:
            raise NetworkError("API request failed") from e

        try:
            return self._handle_response(response)
        except UnauthorizedException as e:
            if not self.bot_info.is_group_bot:
                raise

            # try to refresh access token
            self._access_token = None
            try:
                request.headers.update(await self.get_authorization_header())
            except Exception:
                raise e from None

            # resend request
            try:
                response = await self.adapter.request(request)
            except Exception as ex:
                raise NetworkError("API request failed") from ex

            try:
                return self._handle_response(response)
            except Exception as ex:
                raise ex from None

    # User API
    @API
    async def me(self) -> User:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("users/@me"),
        )
        return parse_obj_as(User, await self._request(request))

    @API
    async def guilds(
        self,
        *,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: Optional[float] = None,
    ) -> List[Guild]:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("users/@me/guilds"),
            params=exclude_none({"before": before, "after": after, "limit": limit}),
        )
        return parse_obj_as(List[Guild], await self._request(request))

    # Guild API
    @API
    async def get_guild(self, *, guild_id: int) -> Guild:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("guilds", str(guild_id)),
        )
        return parse_obj_as(Guild, await self._request(request))

    # Channel API
    @API
    async def get_channels(self, *, guild_id: int) -> List[Channel]:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("guilds", str(guild_id), "channels"),
        )
        return parse_obj_as(List[Channel], await self._request(request))

    @API
    async def get_channel(self, *, channel_id: int) -> Channel:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("channels", str(channel_id)),
        )
        return parse_obj_as(Channel, await self._request(request))

    @API
    async def post_channels(
        self,
        *,
        guild_id: int,
        name: str,
        type: Union[ChannelType, int],
        sub_type: Union[ChannelSubType, int],
        position: Optional[int] = None,
        parent_id: Optional[int] = None,
        private_type: Optional[Union[PrivateType, int]] = None,
        private_user_ids: Optional[List[str]] = None,
        speak_permission: Optional[Union[SpeakPermission, int]] = None,
        application_id: Optional[int] = None,
    ) -> List[Channel]:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("guilds", str(guild_id), "channels"),
            json=exclude_none(
                {
                    "name": name,
                    "type": type,
                    "sub_type": sub_type,
                    "position": position,
                    "parent_id": parent_id,
                    "private_type": private_type,
                    "private_user_ids": private_user_ids,
                    "speaking_permission": speak_permission,
                    "application_id": str(application_id)
                    if application_id is not None
                    else None,
                }
            ),
        )
        return parse_obj_as(List[Channel], await self._request(request))

    @API
    async def patch_channel(
        self,
        *,
        channel_id: int,
        name: Optional[str] = None,
        type: Optional[Union[ChannelType, int]] = None,
        sub_type: Optional[Union[ChannelSubType, int]] = None,
        position: Optional[int] = None,
        parent_id: Optional[int] = None,
        private_type: Optional[int] = None,
        speak_permission: Optional[Union[SpeakPermission, int]] = None,
        application_id: Optional[int] = None,
    ) -> Channel:
        request = Request(
            "PATCH",
            self.adapter.get_api_base().joinpath("channels", str(channel_id)),
            json=exclude_none(
                {
                    "name": name,
                    "type": type,
                    "sub_type": sub_type,
                    "position": position,
                    "parent_id": parent_id,
                    "private_type": private_type,
                    "speaking_permission": speak_permission,
                    "application_id": str(application_id)
                    if application_id is not None
                    else None,
                }
            ),
        )
        return parse_obj_as(Channel, await self._request(request))

    @API
    async def delete_channel(self, *, channel_id: int) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath("channels", str(channel_id)),
        )
        return await self._request(request)

    # Member API
    @API
    async def get_members(
        self,
        *,
        guild_id: int,
        after: Optional[int] = None,
        limit: Optional[float] = None,
    ) -> List[Member]:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("guilds", str(guild_id), "members"),
            params=exclude_none({"after": str(after), "limit": limit}),
        )
        return parse_obj_as(List[Member], await self._request(request))

    @API
    async def get_role_members(
        self,
        *,
        guild_id: int,
        role_id: int,
        start_index: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> GetRoleMembersReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "guilds", str(guild_id), "roles", str(role_id), "members"
            ),
            params=exclude_none({"start_index": start_index, "limit": limit}),
        )
        return parse_obj_as(GetRoleMembersReturn, await self._request(request))

    @API
    async def get_member(self, *, guild_id: int, user_id: int) -> Member:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "guilds", str(guild_id), "members", str(user_id)
            ),
        )
        return parse_obj_as(Member, await self._request(request))

    @API
    async def delete_member(
        self,
        *,
        guild_id: int,
        user_id: int,
        add_blacklist: Optional[bool] = None,
        delete_history_msg_days: Optional[Literal[-1, 0, 3, 7, 15, 30]] = None,
    ) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "guilds", str(guild_id), "members", str(user_id)
            ),
            json=exclude_none(
                {
                    "add_blacklist": add_blacklist,
                    "delete_history_msg_days": delete_history_msg_days,
                }
            ),
        )
        return await self._request(request)

    # Role API
    @API
    async def get_guild_roles(self, *, guild_id: int) -> GetGuildRolesReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("guilds", str(guild_id), "roles"),
        )
        return parse_obj_as(GetGuildRolesReturn, await self._request(request))

    @API
    async def post_guild_role(
        self,
        *,
        guild_id: int,
        name: Optional[str] = None,
        color: Optional[float] = None,
        hoist: Optional[bool] = None,
    ) -> PostGuildRoleReturn:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("guilds", str(guild_id), "roles"),
            json=exclude_none(
                {
                    "name": name,
                    "color": color,
                    "hoist": int(hoist) if hoist is not None else None,
                }
            ),
        )
        return parse_obj_as(PostGuildRoleReturn, await self._request(request))

    @API
    async def patch_guild_role(
        self,
        *,
        guild_id: int,
        role_id: int,
        name: Optional[str] = None,
        color: Optional[float] = None,
        hoist: Optional[bool] = None,
    ) -> PatchGuildRoleReturn:
        request = Request(
            "PATCH",
            self.adapter.get_api_base().joinpath(
                "guilds", str(guild_id), "roles", str(role_id)
            ),
            json=exclude_none(
                {
                    "name": name,
                    "color": color,
                    "hoist": int(hoist) if hoist is not None else None,
                }
            ),
        )
        return parse_obj_as(PatchGuildRoleReturn, await self._request(request))

    @API
    async def delete_guild_role(self, *, guild_id: int, role_id: int) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "guilds", str(guild_id), "roles", str(role_id)
            ),
        )
        return await self._request(request)

    @API
    async def put_guild_member_role(
        self,
        *,
        guild_id: int,
        role_id: int,
        user_id: int,
        channel_id: Optional[int] = None,
    ) -> None:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath(
                "guilds", str(guild_id), "members", str(user_id), "roles", str(role_id)
            ),
            json={"channel": {"id": channel_id}} if channel_id is not None else None,
        )
        return await self._request(request)

    @API
    async def delete_guild_member_role(
        self,
        *,
        guild_id: int,
        role_id: int,
        user_id: int,
        channel_id: Optional[int] = None,
    ) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "guilds", str(guild_id), "members", str(user_id), "roles", str(role_id)
            ),
            json={"channel": {"id": channel_id}} if channel_id is not None else None,
        )
        return await self._request(request)

    # Permission API
    @API
    async def get_channel_permissions(
        self, *, channel_id: int, user_id: int
    ) -> ChannelPermissions:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "members", str(user_id), "permissions"
            ),
        )
        return parse_obj_as(ChannelPermissions, await self._request(request))

    @API
    async def put_channel_permissions(
        self,
        *,
        channel_id: int,
        user_id: int,
        add: Optional[int] = None,
        remove: Optional[int] = None,
    ) -> None:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "members", str(user_id), "permissions"
            ),
            json=exclude_none({"add": str(add), "remove": str(remove)}),
        )
        return await self._request(request)

    @API
    async def get_channel_roles_permissions(
        self, *, channel_id: int, role_id: int
    ) -> ChannelPermissions:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "roles", str(role_id), "permissions"
            ),
        )
        return parse_obj_as(ChannelPermissions, await self._request(request))

    @API
    async def put_channel_roles_permissions(
        self,
        *,
        channel_id: int,
        role_id: int,
        add: Optional[int] = None,
        remove: Optional[int] = None,
    ) -> None:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "roles", str(role_id), "permissions"
            ),
            json=exclude_none({"add": str(add), "remove": str(remove)}),
        )
        return await self._request(request)

    # Message API
    @API
    async def get_message_of_id(
        self, *, channel_id: int, message_id: str
    ) -> GuildMessage:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "messages", str(message_id)
            ),
        )
        result = await self._request(request)
        if isinstance(result, dict) and "message" in result:
            result = result["message"]
        return parse_obj_as(GuildMessage, result)

    @staticmethod
    def _parse_send_message(data: Dict[str, Any]) -> Dict[str, Any]:
        data = exclude_none(data)
        data = {
            k: v.dict(exclude_none=True) if isinstance(v, BaseModel) else v
            for k, v in data.items()
        }
        if file_image := data.pop("file_image", None):
            # 使用 multipart/form-data
            multipart_files: Dict[str, Any] = {"file_image": ("file_image", file_image)}
            multipart_data: Dict[str, Any] = {}
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    # 当字段类型为对象或数组时需要将字段序列化为 JSON 字符串后进行调用
                    # https://bot.q.qq.com/wiki/develop/api/openapi/message/post_messages.html#content-type
                    multipart_files[k] = (
                        k,
                        json.dumps({k: v}).encode("utf-8"),
                        "application/json",
                    )
                else:
                    multipart_data[k] = v
            params = {"files": multipart_files, "data": multipart_data}
        else:
            params = {"json": data}
        return params

    @API
    async def post_messages(
        self,
        *,
        channel_id: int,
        content: Optional[str] = None,
        embed: Optional[MessageEmbed] = None,
        ark: Optional[MessageArk] = None,
        message_reference: Optional[MessageReference] = None,
        image: Optional[str] = None,
        file_image: Optional[Union[bytes, IO[bytes]]] = None,
        markdown: Optional[MessageMarkdown] = None,
        msg_id: Optional[str] = None,
        event_id: Optional[str] = None,
        keyboard: Optional[MessageKeyboard] = None,
    ) -> GuildMessage:
        params = self._parse_send_message(
            {
                "content": content,
                "embed": embed,
                "ark": ark,
                "message_reference": message_reference,
                "image": image,
                "file_image": file_image,
                "markdown": markdown,
                "msg_id": msg_id,
                "event_id": event_id,
                "keyboard": keyboard,
            }
        )
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "messages"
            ),
            **params,
        )
        return parse_obj_as(GuildMessage, await self._request(request))

    @API
    async def delete_message(
        self,
        *,
        channel_id: int,
        message_id: str,
        hidetip: Optional[bool] = None,
    ) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "messages", str(message_id)
            ),
            params={"hidetip": str(hidetip).lower()} if hidetip is not None else None,
        )
        return await self._request(request)

    # Message Setting API
    @API
    async def get_message_setting(self, *, guild_id: int) -> MessageSetting:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "guilds", str(guild_id), "messages", "setting"
            ),
        )
        return parse_obj_as(MessageSetting, await self._request(request))

    # DMS API
    @API
    async def post_dms(self, *, recipient_id: str, source_guild_id: str) -> DMS:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("users", "@me", "dms"),
            json=exclude_none(
                {"recipient_id": recipient_id, "source_guild_id": str(source_guild_id)}
            ),
        )
        return parse_obj_as(DMS, await self._request(request))

    @API
    async def post_dms_messages(
        self,
        *,
        guild_id: int,
        content: Optional[str] = None,
        embed: Optional[MessageEmbed] = None,
        ark: Optional[MessageArk] = None,
        message_reference: Optional[MessageReference] = None,
        image: Optional[str] = None,
        file_image: Optional[Union[bytes, IO[bytes]]] = None,
        markdown: Optional[MessageMarkdown] = None,
        msg_id: Optional[str] = None,
        event_id: Optional[str] = None,
        keyboard: Optional[MessageKeyboard] = None,
    ) -> GuildMessage:
        params = self._parse_send_message(
            {
                "content": content,
                "embed": embed,
                "ark": ark,
                "message_reference": message_reference,
                "image": image,
                "file_image": file_image,
                "markdown": markdown,
                "msg_id": msg_id,
                "event_id": event_id,
                "keyboard": keyboard,
            }
        )
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("dms", str(guild_id), "messages"),
            **params,
        )
        return parse_obj_as(GuildMessage, await self._request(request))

    @API
    async def delete_dms_message(
        self, *, guild_id: int, message_id: str, hidetip: Optional[bool] = None
    ) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "dms", str(guild_id), "messages", str(message_id)
            ),
            params={"hidetip": str(hidetip).lower()} if hidetip is not None else None,
        )
        return await self._request(request)

    # Mute API
    @API
    async def patch_guild_mute(
        self,
        *,
        guild_id: int,
        mute_end_timestamp: Optional[Union[int, datetime]] = None,
        mute_seconds: Optional[Union[int, timedelta]] = None,
    ) -> None:
        if isinstance(mute_end_timestamp, datetime):
            mute_end_timestamp = int(mute_end_timestamp.timestamp())

        if isinstance(mute_seconds, timedelta):
            mute_seconds = int(mute_seconds.total_seconds())

        request = Request(
            "PATCH",
            self.adapter.get_api_base().joinpath("guilds", str(guild_id), "mute"),
            json=exclude_none(
                {
                    "mute_end_timestamp": str(mute_end_timestamp),
                    "mute_seconds": str(mute_seconds),
                }
            ),
        )
        return await self._request(request)

    @API
    async def patch_guild_member_mute(
        self,
        *,
        guild_id: int,
        user_id: int,
        mute_end_timestamp: Optional[Union[int, datetime]] = None,
        mute_seconds: Optional[Union[int, timedelta]] = None,
    ) -> None:
        if isinstance(mute_end_timestamp, datetime):
            mute_end_timestamp = int(mute_end_timestamp.timestamp())

        if isinstance(mute_seconds, timedelta):
            mute_seconds = int(mute_seconds.total_seconds())

        request = Request(
            "PATCH",
            self.adapter.get_api_base().joinpath(
                "guilds", str(guild_id), "members", str(user_id), "mute"
            ),
            json=exclude_none(
                {
                    "mute_end_timestamp": str(mute_end_timestamp),
                    "mute_seconds": str(mute_seconds),
                }
            ),
        )
        return await self._request(request)

    @API
    async def patch_guild_mute_multi_member(
        self,
        *,
        guild_id: int,
        user_ids: List[int],
        mute_end_timestamp: Optional[Union[int, datetime]] = None,
        mute_seconds: Optional[Union[int, timedelta]] = None,
    ) -> List[int]:
        if isinstance(mute_end_timestamp, datetime):
            mute_end_timestamp = int(mute_end_timestamp.timestamp())

        if isinstance(mute_seconds, timedelta):
            mute_seconds = int(mute_seconds.total_seconds())

        request = Request(
            "PATCH",
            self.adapter.get_api_base().joinpath("guilds", str(guild_id), "mute"),
            json=exclude_none(
                {
                    "user_ids": [str(u) for u in user_ids],
                    "mute_end_timestamp": str(mute_end_timestamp),
                    "mute_seconds": str(mute_seconds),
                }
            ),
        )
        return parse_obj_as(List[int], await self._request(request))

    # Announce API
    @API
    async def post_guild_announces(
        self,
        *,
        guild_id: int,
        message_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        announces_type: Optional[int] = None,
        recommend_channels: Optional[List[RecommendChannel]] = None,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("guilds", str(guild_id), "announces"),
            json=exclude_none(
                {
                    "message_id": message_id,
                    "channel_id": channel_id,
                    "announces_type": announces_type,
                    "recommend_channels": (
                        [r.dict(exclude_none=True) for r in recommend_channels]
                        if recommend_channels is not None
                        else None
                    ),
                }
            ),
        )
        return await self._request(request)

    @API
    async def delete_guild_announces(self, *, guild_id: int, message_id: str) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "guilds", str(guild_id), "announces", str(message_id)
            ),
        )
        return await self._request(request)

    # Pins API
    @API
    async def put_pins_message(
        self, *, channel_id: int, message_id: str
    ) -> PinsMessage:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "pins", str(message_id)
            ),
        )
        return parse_obj_as(PinsMessage, await self._request(request))

    @API
    async def delete_pins_message(self, *, channel_id: int, message_id: str) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "pins", str(message_id)
            ),
        )
        return await self._request(request)

    @API
    async def get_pins_message(self, *, channel_id: int) -> PinsMessage:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("channels", str(channel_id), "pins"),
        )
        return parse_obj_as(PinsMessage, await self._request(request))

    # Schedule API
    @API
    async def get_schedules(
        self, *, channel_id: int, since: Optional[Union[int, datetime]] = None
    ) -> List[Schedule]:
        if isinstance(since, datetime):
            since = int(since.timestamp() * 1000)

        request = Request(
            "GET",
            self.adapter.get_api_base() / f"channels/{channel_id}/schedules",
            json=exclude_none({"since": since}),
        )
        return parse_obj_as(List[Schedule], await self._request(request))

    @API
    async def get_schedule(self, *, channel_id: int, schedule_id: str) -> Schedule:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "schedules", schedule_id
            ),
        )
        return parse_obj_as(Schedule, await self._request(request))

    @API
    async def post_schedule(
        self,
        *,
        channel_id: int,
        name: str,
        description: Optional[str] = None,
        start_timestamp: Union[int, datetime],
        end_timestamp: Union[int, datetime],
        jump_channel_id: Optional[int] = None,
        remind_type: Union[RemindType, int],
    ) -> Schedule:
        if isinstance(start_timestamp, datetime):
            start_timestamp = int(start_timestamp.timestamp() * 1000)

        if isinstance(end_timestamp, datetime):
            end_timestamp = int(end_timestamp.timestamp() * 1000)

        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "schedules"
            ),
            json={
                "schedule": exclude_none(
                    {
                        "name": name,
                        "description": description,
                        "start_timestamp": start_timestamp,
                        "end_timestamp": end_timestamp,
                        "jump_channel_id": jump_channel_id,
                        "remind_type": remind_type,
                    }
                )
            },
        )
        return parse_obj_as(Schedule, await self._request(request))

    @API
    async def patch_schedule(
        self,
        *,
        channel_id: int,
        schedule_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_timestamp: Optional[Union[int, datetime]] = None,
        end_timestamp: Optional[Union[int, datetime]] = None,
        jump_channel_id: Optional[int] = None,
        remind_type: Optional[str] = None,
    ) -> Schedule:
        if isinstance(start_timestamp, datetime):
            start_timestamp = int(start_timestamp.timestamp() * 1000)

        if isinstance(end_timestamp, datetime):
            end_timestamp = int(end_timestamp.timestamp() * 1000)

        request = Request(
            "PATCH",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "schedules", schedule_id
            ),
            json={
                "schedule": exclude_none(
                    {
                        "name": name,
                        "description": description,
                        "start_timestamp": start_timestamp,
                        "end_timestamp": end_timestamp,
                        "jump_channel_id": jump_channel_id,
                        "remind_type": remind_type,
                    }
                )
            },
        )
        return parse_obj_as(Schedule, await self._request(request))

    @API
    async def delete_schedule(self, *, channel_id: int, schedule_id: str) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "schedules", schedule_id
            ),
        )
        return await self._request(request)

    @API
    async def put_message_reaction(
        self, *, channel_id: int, message_id: str, type: Union[EmojiType, int], id: str
    ) -> None:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath(
                "channels",
                str(channel_id),
                "messages",
                message_id,
                "reactions",
                str(type),
                id,
            ),
        )
        return await self._request(request)

    @API
    async def delete_own_message_reaction(
        self, *, channel_id: int, message_id: str, type: Union[EmojiType, int], id: str
    ) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "channels",
                str(channel_id),
                "messages",
                message_id,
                "reactions",
                str(type),
                id,
            ),
        )
        return await self._request(request)

    @API
    async def get_reaction_users(
        self,
        *,
        channel_id: int,
        message_id: str,
        type: Union[EmojiType, int],
        id: str,
        cookie: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> GetReactionUsersReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "channels",
                str(channel_id),
                "messages",
                message_id,
                "reactions",
                str(type),
                id,
            ),
            params=exclude_none({"cookie": cookie, "limit": limit}),
        )
        return await self._request(request)

    # Audio API
    @API
    async def audio_control(
        self,
        *,
        channel_id: int,
        audio_url: Optional[str] = None,
        text: Optional[str] = None,
        status: Union[AudioStatus, int],
    ) -> Dict[Never, Never]:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("channels", str(channel_id), "audio"),
            json=AudioControl(audio_url=audio_url, text=text, status=status).dict(
                exclude_none=True
            ),
        )
        return await self._request(request)

    @API
    async def put_mic(self, *, channel_id: int) -> Dict[Never, Never]:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath("channels", str(channel_id), "mic"),
        )
        return await self._request(request)

    @API
    async def delete_mic(self, *, channel_id: int) -> Dict[Never, Never]:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath("channels", str(channel_id), "mic"),
        )
        return await self._request(request)

    # Forum API
    @API
    async def get_threads_list(self, *, channel_id: int) -> GetThreadsListReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "threads"
            ),
        )
        return parse_obj_as(GetThreadsListReturn, await self._request(request))

    @API
    async def get_thread(self, *, channel_id: int, thread_id: str) -> GetThreadReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "threads", thread_id
            ),
        )
        return parse_obj_as(GetThreadReturn, await self._request(request))

    @overload
    async def put_thread(
        self,
        *,
        channel_id: int,
        title: str,
        content: str,
        format: Literal[1, 2, 3],
    ) -> PutThreadReturn:
        ...

    @overload
    async def put_thread(
        self,
        *,
        channel_id: int,
        title: str,
        content: RichText,
        format: Literal[4],
    ) -> PutThreadReturn:
        ...

    @API
    async def put_thread(
        self,
        *,
        channel_id: int,
        title: str,
        content: Union[str, RichText],
        format: Literal[1, 2, 3, 4],
    ) -> PutThreadReturn:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "threads"
            ),
            json=exclude_none(
                {
                    "title": title,
                    "content": (
                        content.json(exclude_none=True)
                        if isinstance(content, RichText)
                        else content
                    ),
                    "format": format,
                }
            ),
        )
        return parse_obj_as(PutThreadReturn, await self._request(request))

    @API
    async def delete_thread(self, *, channel_id: int, thread_id: str) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "channels", str(channel_id), "threads", thread_id
            ),
        )
        return await self._request(request)

    # API Permission API
    @API
    async def get_guild_api_permission(
        self, *, guild_id: int
    ) -> GetGuildAPIPermissionReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "guilds", str(guild_id), "api_permission"
            ),
        )
        return parse_obj_as(GetGuildAPIPermissionReturn, await self._request(request))

    @API
    async def post_api_permission_demand(
        self,
        *,
        guild_id: int,
        channel_id: int,
        api_identify: APIPermissionDemandIdentify,
        desc: str,
    ) -> APIPermissionDemand:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath(
                "guilds", str(guild_id), "api_permission", "demand"
            ),
            json=exclude_none(
                {
                    "channel_id": str(channel_id),
                    "api_identify": api_identify.dict(exclude_none=True),
                    "desc": desc,
                }
            ),
        )
        return parse_obj_as(APIPermissionDemand, await self._request(request))

    # WebSocket API
    @API
    async def url_get(self) -> UrlGetReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("gateway"),
        )
        return parse_obj_as(UrlGetReturn, await self._request(request))

    @API
    async def shard_url_get(self) -> ShardUrlGetReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("gateway", "bot"),
        )
        return parse_obj_as(ShardUrlGetReturn, await self._request(request))
