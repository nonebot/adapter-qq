from base64 import b64encode
from contextlib import suppress
from datetime import datetime, timedelta, timezone
import json
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Literal,
    NoReturn,
    Optional,
    Union,
    cast,
    overload,
)
from typing_extensions import Never, override

from pydantic import BaseModel

from nonebot.adapters import Bot as BaseBot
from nonebot.compat import type_validate_python
from nonebot.drivers import Request, Response
from nonebot.message import handle_event

from .config import BotInfo
from .event import (
    C2CMessageCreateEvent,
    DirectMessageCreateEvent,
    Event,
    GroupAtMessageCreateEvent,
    GuildMessageEvent,
    InteractionCreateEvent,
    QQMessageEvent,
    ReadyEvent,
)
from .exception import (
    ActionFailed,
    ApiNotAvailable,
    AuditException,
    NetworkError,
    RateLimitException,
    UnauthorizedException,
)
from .message import Message, MessageSegment
from .models import (
    DMS,
    APIPermissionDemand,
    APIPermissionDemandIdentify,
    AudioControl,
    AudioStatus,
    Channel,
    ChannelPermissions,
    ChannelSubType,
    ChannelType,
    Dispatch,
    EmojiType,
    GetGuildAPIPermissionReturn,
    GetGuildRolesReturn,
    GetReactionUsersReturn,
    GetRoleMembersReturn,
    GetThreadReturn,
    GetThreadsListReturn,
    Guild,
    Media,
    Member,
    MessageActionButton,
    MessageArk,
    MessageEmbed,
    MessageKeyboard,
    MessageMarkdown,
    MessagePromptKeyboard,
    MessageReference,
    MessageSetting,
    MessageStream,
    PatchGuildRoleReturn,
    PinsMessage,
    PostC2CFilesReturn,
    PostC2CMessagesReturn,
    PostGroupFilesReturn,
    PostGroupMembersReturn,
    PostGroupMessagesReturn,
    PostGuildRoleReturn,
    PrivateType,
    PutThreadReturn,
    RecommendChannel,
    RemindType,
    RichText,
    Schedule,
    ShardUrlGetReturn,
    SpeakPermission,
    UrlGetReturn,
    User,
)
from .models import Message as GuildMessage
from .utils import API, exclude_none, log

if TYPE_CHECKING:
    from .adapter import Adapter


async def _check_reply(
    bot: "Bot",
    event: Union[GuildMessageEvent, QQMessageEvent],
) -> None:
    """检查消息中存在的回复，赋值 `event.reply`, `event.to_me`。

    参数:
        bot: Bot 对象
        event: MessageEvent 对象
    """
    if not isinstance(event, GuildMessageEvent) or event.message_reference is None:
        return
    try:
        event.reply = await bot.get_message_of_id(
            channel_id=event.channel_id,
            message_id=event.message_reference.message_id,
        )
        if event.reply.author.id == bot.self_info.id:
            event.to_me = True
    except Exception as e:
        log("WARNING", f"Error when getting message reply info: {e!r}", e)


def _check_at_me(
    bot: "Bot",
    event: Union[GuildMessageEvent, QQMessageEvent],
):
    if (
        isinstance(event, GuildMessageEvent)
        and event.mentions is not None
        and bot.self_info.id in {user.id for user in event.mentions}
    ):
        event.to_me = True

    def _is_at_me_seg(segment: MessageSegment) -> bool:
        return (
            segment.type == "mention_user"
            and segment.data.get("user_id") == bot.self_info.id
        )

    message = event.get_message()

    # ensure message is not empty
    if not message:
        message.append(MessageSegment.text(""))

    deleted = False
    if _is_at_me_seg(message[0]):
        message.pop(0)
        deleted = True
        event.to_me = True
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
            event.to_me = True
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

    @self_info.setter
    def self_info(self, info: User):
        self._self_info = info

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
            if (
                not isinstance(data, dict)
                or "access_token" not in data
                or "expires_in" not in data
            ):
                raise NetworkError(
                    f"Get authorization failed with invalid response {data!r}."
                    " Please check your config."
                )
            self._access_token = cast(str, data["access_token"])
            self._expires_in = datetime.now(timezone.utc) + timedelta(
                seconds=int(data["expires_in"])
            )
        return self._access_token

    async def _get_authorization_header(self) -> str:
        """获取当前 Bot 的鉴权信息"""
        return f"QQBot {await self.get_access_token()}"

    async def get_authorization_header(self) -> dict[str, str]:
        """获取当前 Bot 的鉴权信息"""
        return {
            "Authorization": await self._get_authorization_header(),
            "X-Union-Appid": self.bot_info.id,
        }

    async def handle_event(self, event: Event) -> None:
        if isinstance(event, (GuildMessageEvent, QQMessageEvent)):
            await _check_reply(self, event)
            _check_at_me(self, event)
        await handle_event(self, event)

    @staticmethod
    def _prepare_message(message: Union[str, Message, MessageSegment]) -> Message:
        _message = MessageSegment.text(message) if isinstance(message, str) else message
        _message = _message if isinstance(_message, Message) else Message(_message)
        return _message

    @staticmethod
    def _extract_send_message(
        message: Message, escape_text: bool = True
    ) -> dict[str, Any]:
        kwargs = {}
        content = message.extract_content(escape_text) or None
        kwargs["content"] = content
        if embed := (message["embed"] or None):
            kwargs["embed"] = embed[-1].data["embed"]
        if ark := (message["ark"] or None):
            kwargs["ark"] = ark[-1].data["ark"]
        if markdown := (message["markdown"] or None):
            kwargs["markdown"] = markdown[-1].data["markdown"]
        if reference := (message["reference"] or None):
            kwargs["message_reference"] = reference[-1].data["reference"]
        if keyboard := (message["keyboard"] or None):
            kwargs["keyboard"] = keyboard[-1].data["keyboard"]
        if stream := (message["stream"] or None):
            kwargs["stream"] = stream[-1].data["stream"]
        if prompt_keyboard := (message["prompt_keyboard"] or None):
            kwargs["prompt_keyboard"] = prompt_keyboard[-1].data["prompt_keyboard"]
        if action_button := (message["action_button"] or None):
            kwargs["action_button"] = action_button[-1].data["action_button"]
        return kwargs

    @staticmethod
    def _extract_guild_image(message: Message) -> dict[str, Any]:
        kwargs = {}
        if image := (message["image"] or None):
            kwargs["image"] = image[-1].data["url"]
        if file_image := (message["file_image"] or None):
            kwargs["file_image"] = file_image[-1].data["content"]
        return kwargs

    @staticmethod
    def _extract_qq_media(message: Message) -> dict[str, Any]:
        kwargs = {}
        if image := message["image"]:
            kwargs["file_type"] = 1
            kwargs["url"] = image[-1].data["url"]
        elif video := message["video"]:
            kwargs["file_type"] = 2
            kwargs["url"] = video[-1].data["url"]
        elif audio := message["audio"]:
            kwargs["file_type"] = 3
            kwargs["url"] = audio[-1].data["url"]
        elif file := message["file"]:
            kwargs["file_type"] = 4
            kwargs["url"] = file[-1].data["url"]
        elif file_image := message["file_image"]:
            kwargs["file_type"] = 1
            kwargs["file_data"] = file_image[-1].data["content"]
        elif file_video := message["file_video"]:
            kwargs["file_type"] = 2
            kwargs["file_data"] = file_video[-1].data["content"]
        elif file_audio := message["file_audio"]:
            kwargs["file_type"] = 3
            kwargs["file_data"] = file_audio[-1].data["content"]
        elif file_file := message["file_file"]:
            kwargs["file_type"] = 4
            kwargs["file_data"] = file_file[-1].data["content"]
        return kwargs

    async def send_to_dms(
        self,
        guild_id: str,
        message: Union[str, Message, MessageSegment],
        msg_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> GuildMessage:
        message = self._prepare_message(message)
        return await self.post_dms_messages(
            guild_id=guild_id,
            msg_id=msg_id,
            event_id=event_id,
            **self._extract_send_message(message=message, escape_text=True),
            **self._extract_guild_image(message=message),
        )

    async def send_to_channel(
        self,
        channel_id: str,
        message: Union[str, Message, MessageSegment],
        msg_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> GuildMessage:
        message = self._prepare_message(message)
        return await self.post_messages(
            channel_id=channel_id,
            msg_id=msg_id,
            event_id=event_id,
            **self._extract_send_message(message=message, escape_text=True),
            **self._extract_guild_image(message=message),
        )

    async def send_to_c2c(
        self,
        openid: str,
        message: Union[str, Message, MessageSegment],
        msg_id: Optional[str] = None,
        msg_seq: Optional[int] = None,
        event_id: Optional[str] = None,
    ) -> Union[PostC2CMessagesReturn, PostC2CFilesReturn]:
        message = self._prepare_message(message)
        kwargs = self._extract_send_message(message=message, escape_text=False)
        if kwargs.get("embed"):
            msg_type = 4
        elif kwargs.get("ark"):
            msg_type = 3
        elif (
            kwargs.get("markdown")
            or kwargs.get("keyboard")
            or kwargs.get("prompt_keyboard")
            or kwargs.get("action_button")
        ):
            msg_type = 2
        elif (
            message["image"]
            or message["audio"]
            or message["video"]
            or message["file"]
            or message["file_image"]
            or message["file_audio"]
            or message["file_video"]
            or message["file_file"]
        ):
            msg_type = 7
        else:
            msg_type = 0

        media: Optional[Media] = None
        if msg_type == 7:
            media_info = await self.post_c2c_files(
                openid=openid, srv_send_msg=False, **self._extract_qq_media(message)
            )
            media = (
                Media(file_info=media_info.file_info) if media_info.file_info else None
            )
        kwargs["media"] = media

        return await self.post_c2c_messages(
            openid=openid,
            msg_type=msg_type,
            msg_id=msg_id,
            msg_seq=msg_seq,
            event_id=event_id,
            **kwargs,
        )

    async def send_to_group(
        self,
        group_openid: str,
        message: Union[str, Message, MessageSegment],
        msg_id: Optional[str] = None,
        msg_seq: Optional[int] = None,
        event_id: Optional[str] = None,
    ) -> Union[PostGroupMessagesReturn, PostGroupFilesReturn]:
        message = self._prepare_message(message)
        kwargs = self._extract_send_message(message=message, escape_text=False)
        if kwargs.get("embed"):
            msg_type = 4
        elif kwargs.get("ark"):
            msg_type = 3
        elif kwargs.get("markdown") or kwargs.get("keyboard"):
            msg_type = 2
        elif (
            message["image"]
            or message["audio"]
            or message["video"]
            or message["file"]
            or message["file_image"]
            or message["file_audio"]
            or message["file_video"]
            or message["file_file"]
        ):
            msg_type = 7
        else:
            msg_type = 0

        media: Optional[Media] = None
        if msg_type == 7:
            media_info = await self.post_group_files(
                group_openid=group_openid,
                srv_send_msg=False,
                **self._extract_qq_media(message),
            )
            media = (
                Media(file_info=media_info.file_info) if media_info.file_info else None
            )
        kwargs["media"] = media

        return await self.post_group_messages(
            group_openid=group_openid,
            msg_type=msg_type,
            msg_id=msg_id,
            msg_seq=msg_seq,
            event_id=event_id,
            **kwargs,
        )

    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs,
    ) -> Any:
        if isinstance(event, DirectMessageCreateEvent):
            # 私信需要使用 post_dms_messages
            # https://bot.q.qq.com/wiki/develop/api/openapi/dms/post_dms_messages.html#%E5%8F%91%E9%80%81%E7%A7%81%E4%BF%A1
            return await self.send_to_dms(
                guild_id=event.guild_id,
                message=message,
                msg_id=event.id,
            )
        elif isinstance(event, GuildMessageEvent):
            return await self.send_to_channel(
                channel_id=event.channel_id,
                message=message,
                msg_id=event.id,
            )
        elif isinstance(event, C2CMessageCreateEvent):
            event._reply_seq += 1
            return await self.send_to_c2c(
                openid=event.author.id,
                message=message,
                msg_id=event.id,
                msg_seq=event._reply_seq,
            )
        elif isinstance(event, GroupAtMessageCreateEvent):
            event._reply_seq += 1
            return await self.send_to_group(
                group_openid=event.group_openid,
                message=message,
                msg_id=event.id,
                msg_seq=event._reply_seq,
            )
        elif isinstance(event, InteractionCreateEvent):
            if gid := event.group_openid:
                return await self.send_to_group(
                    group_openid=gid, event_id=event.event_id, message=message
                )
            elif cid := event.channel_id:
                return await self.send_to_channel(
                    channel_id=cid, event_id=event.event_id, message=message
                )
            elif uid := event.user_openid:
                return await self.send_to_c2c(
                    openid=uid, event_id=event.event_id, message=message
                )
            elif gid := event.guild_id:
                return await self.send_to_dms(
                    guild_id=gid, event_id=event.event_id, message=message
                )

        raise RuntimeError("Event cannot be replied to!")

    # API request methods
    def _handle_audit(self, response: Response) -> None:
        if 200 <= response.status_code <= 202:
            with suppress(json.JSONDecodeError):
                if (
                    response.content
                    and (content := json.loads(response.content))
                    and isinstance(content, dict)
                    and (
                        audit_id := (
                            content.get("data", {})
                            .get("message_audit", {})
                            .get("audit_id", None)
                        )
                    )
                ):
                    raise AuditException(audit_id)

    def _handle_response(self, response: Response) -> Any:
        if trace_id := response.headers.get("X-Tps-trace-ID", None):
            log(
                "TRACE",
                f"Called API {response.request and response.request.url} "
                f"response {response.status_code} with trace id {trace_id}",
            )

        self._handle_audit(response)

        if response.status_code == 201 or response.status_code == 202:
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
            log("DEBUG", "Access token expired, try to refresh it.")

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
        return type_validate_python(User, await self._request(request))

    @API
    async def guilds(
        self,
        *,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: Optional[float] = None,
    ) -> list[Guild]:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("users", "@me", "guilds"),
            params=exclude_none({"before": before, "after": after, "limit": limit}),
        )
        return type_validate_python(list[Guild], await self._request(request))

    # Guild API
    @API
    async def get_guild(self, *, guild_id: str) -> Guild:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("guilds", guild_id),
        )
        return type_validate_python(Guild, await self._request(request))

    # Channel API
    @API
    async def get_channels(self, *, guild_id: str) -> list[Channel]:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("guilds", guild_id, "channels"),
        )
        return type_validate_python(list[Channel], await self._request(request))

    @API
    async def get_channel(self, *, channel_id: str) -> Channel:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("channels", channel_id),
        )
        return type_validate_python(Channel, await self._request(request))

    @API
    async def post_channels(
        self,
        *,
        guild_id: str,
        name: str,
        type: Union[ChannelType, int],
        sub_type: Union[ChannelSubType, int],
        position: Optional[int] = None,
        parent_id: Optional[int] = None,
        private_type: Optional[Union[PrivateType, int]] = None,
        private_user_ids: Optional[list[str]] = None,
        speak_permission: Optional[Union[SpeakPermission, int]] = None,
        application_id: Optional[str] = None,
    ) -> list[Channel]:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("guilds", guild_id, "channels"),
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
                    "application_id": application_id,
                }
            ),
        )
        return type_validate_python(list[Channel], await self._request(request))

    @API
    async def patch_channel(
        self,
        *,
        channel_id: str,
        name: Optional[str] = None,
        type: Optional[Union[ChannelType, int]] = None,
        sub_type: Optional[Union[ChannelSubType, int]] = None,
        position: Optional[int] = None,
        parent_id: Optional[int] = None,
        private_type: Optional[int] = None,
        speak_permission: Optional[Union[SpeakPermission, int]] = None,
        application_id: Optional[str] = None,
    ) -> Channel:
        request = Request(
            "PATCH",
            self.adapter.get_api_base().joinpath("channels", channel_id),
            json=exclude_none(
                {
                    "name": name,
                    "type": type,
                    "sub_type": sub_type,
                    "position": position,
                    "parent_id": parent_id,
                    "private_type": private_type,
                    "speaking_permission": speak_permission,
                    "application_id": application_id,
                }
            ),
        )
        return type_validate_python(Channel, await self._request(request))

    @API
    async def delete_channel(self, *, channel_id: str) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath("channels", channel_id),
        )
        return await self._request(request)

    # Member API
    @API
    async def get_members(
        self,
        *,
        guild_id: str,
        after: Optional[str] = None,
        limit: Optional[float] = None,
    ) -> list[Member]:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("guilds", guild_id, "members"),
            params=exclude_none({"after": after, "limit": limit}),
        )
        return type_validate_python(list[Member], await self._request(request))

    @API
    async def get_role_members(
        self,
        *,
        guild_id: str,
        role_id: str,
        start_index: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> GetRoleMembersReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "guilds", guild_id, "roles", role_id, "members"
            ),
            params=exclude_none({"start_index": start_index, "limit": limit}),
        )
        return type_validate_python(GetRoleMembersReturn, await self._request(request))

    @API
    async def get_member(self, *, guild_id: str, user_id: str) -> Member:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "guilds", guild_id, "members", user_id
            ),
        )
        return type_validate_python(Member, await self._request(request))

    @API
    async def delete_member(
        self,
        *,
        guild_id: str,
        user_id: str,
        add_blacklist: Optional[bool] = None,
        delete_history_msg_days: Optional[Literal[-1, 0, 3, 7, 15, 30]] = None,
    ) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "guilds", guild_id, "members", user_id
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
    async def get_guild_roles(self, *, guild_id: str) -> GetGuildRolesReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("guilds", guild_id, "roles"),
        )
        return type_validate_python(GetGuildRolesReturn, await self._request(request))

    @API
    async def post_guild_role(
        self,
        *,
        guild_id: str,
        name: Optional[str] = None,
        color: Optional[float] = None,
        hoist: Optional[bool] = None,
    ) -> PostGuildRoleReturn:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("guilds", guild_id, "roles"),
            json=exclude_none(
                {
                    "name": name,
                    "color": color,
                    "hoist": int(hoist) if hoist is not None else None,
                }
            ),
        )
        return type_validate_python(PostGuildRoleReturn, await self._request(request))

    @API
    async def patch_guild_role(
        self,
        *,
        guild_id: str,
        role_id: str,
        name: Optional[str] = None,
        color: Optional[float] = None,
        hoist: Optional[bool] = None,
    ) -> PatchGuildRoleReturn:
        request = Request(
            "PATCH",
            self.adapter.get_api_base().joinpath("guilds", guild_id, "roles", role_id),
            json=exclude_none(
                {
                    "name": name,
                    "color": color,
                    "hoist": int(hoist) if hoist is not None else None,
                }
            ),
        )
        return type_validate_python(PatchGuildRoleReturn, await self._request(request))

    @API
    async def delete_guild_role(self, *, guild_id: str, role_id: str) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath("guilds", guild_id, "roles", role_id),
        )
        return await self._request(request)

    @API
    async def put_guild_member_role(
        self,
        *,
        guild_id: str,
        role_id: str,
        user_id: str,
        channel_id: Optional[str] = None,
    ) -> None:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath(
                "guilds", guild_id, "members", user_id, "roles", role_id
            ),
            json={"channel": {"id": channel_id}} if channel_id is not None else None,
        )
        return await self._request(request)

    @API
    async def delete_guild_member_role(
        self,
        *,
        guild_id: str,
        role_id: str,
        user_id: str,
        channel_id: Optional[str] = None,
    ) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "guilds", guild_id, "members", user_id, "roles", role_id
            ),
            json={"channel": {"id": channel_id}} if channel_id is not None else None,
        )
        return await self._request(request)

    # Permission API
    @API
    async def get_channel_permissions(
        self, *, channel_id: str, user_id: str
    ) -> ChannelPermissions:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "members", user_id, "permissions"
            ),
        )
        return type_validate_python(ChannelPermissions, await self._request(request))

    @API
    async def put_channel_permissions(
        self,
        *,
        channel_id: str,
        user_id: str,
        add: Optional[int] = None,
        remove: Optional[int] = None,
    ) -> None:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "members", user_id, "permissions"
            ),
            json=exclude_none({"add": str(add), "remove": str(remove)}),
        )
        return await self._request(request)

    @API
    async def get_channel_roles_permissions(
        self, *, channel_id: str, role_id: str
    ) -> ChannelPermissions:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "roles", role_id, "permissions"
            ),
        )
        return type_validate_python(ChannelPermissions, await self._request(request))

    @API
    async def put_channel_roles_permissions(
        self,
        *,
        channel_id: str,
        role_id: str,
        add: Optional[int] = None,
        remove: Optional[int] = None,
    ) -> None:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "roles", role_id, "permissions"
            ),
            json=exclude_none({"add": str(add), "remove": str(remove)}),
        )
        return await self._request(request)

    # Message API
    @API
    async def get_message_of_id(
        self, *, channel_id: str, message_id: str
    ) -> GuildMessage:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "messages", message_id
            ),
        )
        result = await self._request(request)
        if isinstance(result, dict) and "message" in result:
            result = result["message"]
        return type_validate_python(GuildMessage, result)

    @staticmethod
    def _parse_send_message(data: dict[str, Any]) -> dict[str, Any]:
        data = exclude_none(data)
        data = {
            k: v.dict(exclude_none=True) if isinstance(v, BaseModel) else v
            for k, v in data.items()
        }
        if file_image := data.pop("file_image", None):
            # 使用 multipart/form-data
            multipart_files: dict[str, Any] = {"file_image": ("file_image", file_image)}
            multipart_data: dict[str, Any] = {}
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
        channel_id: str,
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
            self.adapter.get_api_base().joinpath("channels", channel_id, "messages"),
            **params,
        )
        return type_validate_python(GuildMessage, await self._request(request))

    @API
    async def delete_message(
        self,
        *,
        channel_id: str,
        message_id: str,
        hidetip: Optional[bool] = None,
    ) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "messages", message_id
            ),
            params={"hidetip": str(hidetip).lower()} if hidetip is not None else None,
        )
        return await self._request(request)

    # Message Setting API
    @API
    async def get_message_setting(self, *, guild_id: str) -> MessageSetting:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "guilds", guild_id, "message", "setting"
            ),
        )
        return type_validate_python(MessageSetting, await self._request(request))

    # DMS API
    @API
    async def post_dms(self, *, recipient_id: str, source_guild_id: str) -> DMS:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("users", "@me", "dms"),
            json=exclude_none(
                {"recipient_id": recipient_id, "source_guild_id": source_guild_id}
            ),
        )
        return type_validate_python(DMS, await self._request(request))

    @API
    async def post_dms_messages(
        self,
        *,
        guild_id: str,
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
            self.adapter.get_api_base().joinpath("dms", guild_id, "messages"),
            **params,
        )
        return type_validate_python(GuildMessage, await self._request(request))

    @API
    async def delete_dms_message(
        self, *, guild_id: str, message_id: str, hidetip: Optional[bool] = None
    ) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "dms", guild_id, "messages", message_id
            ),
            params={"hidetip": str(hidetip).lower()} if hidetip is not None else None,
        )
        return await self._request(request)

    # Mute API
    @API
    async def patch_guild_mute(
        self,
        *,
        guild_id: str,
        mute_end_timestamp: Optional[Union[int, datetime]] = None,
        mute_seconds: Optional[Union[int, timedelta]] = None,
    ) -> None:
        if isinstance(mute_end_timestamp, datetime):
            mute_end_timestamp = int(mute_end_timestamp.timestamp())

        if isinstance(mute_seconds, timedelta):
            mute_seconds = int(mute_seconds.total_seconds())

        request = Request(
            "PATCH",
            self.adapter.get_api_base().joinpath("guilds", guild_id, "mute"),
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
        guild_id: str,
        user_id: str,
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
                "guilds", guild_id, "members", user_id, "mute"
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
        guild_id: str,
        user_ids: list[str],
        mute_end_timestamp: Optional[Union[int, datetime]] = None,
        mute_seconds: Optional[Union[int, timedelta]] = None,
    ) -> list[int]:
        if isinstance(mute_end_timestamp, datetime):
            mute_end_timestamp = int(mute_end_timestamp.timestamp())

        if isinstance(mute_seconds, timedelta):
            mute_seconds = int(mute_seconds.total_seconds())

        request = Request(
            "PATCH",
            self.adapter.get_api_base().joinpath("guilds", guild_id, "mute"),
            json=exclude_none(
                {
                    "user_ids": user_ids,
                    "mute_end_timestamp": str(mute_end_timestamp),
                    "mute_seconds": str(mute_seconds),
                }
            ),
        )
        return type_validate_python(list[int], await self._request(request))

    # Announce API
    @API
    async def post_guild_announces(
        self,
        *,
        guild_id: str,
        message_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        announces_type: Optional[int] = None,
        recommend_channels: Optional[list[RecommendChannel]] = None,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("guilds", guild_id, "announces"),
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
    async def delete_guild_announces(self, *, guild_id: str, message_id: str) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "guilds", guild_id, "announces", message_id
            ),
        )
        return await self._request(request)

    # Pins API
    @API
    async def put_pins_message(
        self, *, channel_id: str, message_id: str
    ) -> PinsMessage:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "pins", message_id
            ),
        )
        return type_validate_python(PinsMessage, await self._request(request))

    @API
    async def delete_pins_message(self, *, channel_id: str, message_id: str) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "pins", message_id
            ),
        )
        return await self._request(request)

    @API
    async def get_pins_message(self, *, channel_id: str) -> PinsMessage:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("channels", channel_id, "pins"),
        )
        return type_validate_python(PinsMessage, await self._request(request))

    # Schedule API
    @API
    async def get_schedules(
        self, *, channel_id: str, since: Optional[Union[int, datetime]] = None
    ) -> list[Schedule]:
        if isinstance(since, datetime):
            since = int(since.timestamp() * 1000)

        request = Request(
            "GET",
            self.adapter.get_api_base() / f"channels/{channel_id}/schedules",
            json=exclude_none({"since": since}),
        )
        return type_validate_python(list[Schedule], await self._request(request))

    @API
    async def get_schedule(self, *, channel_id: str, schedule_id: str) -> Schedule:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "schedules", schedule_id
            ),
        )
        return type_validate_python(Schedule, await self._request(request))

    @API
    async def post_schedule(
        self,
        *,
        channel_id: str,
        name: str,
        description: Optional[str] = None,
        start_timestamp: Union[int, datetime],
        end_timestamp: Union[int, datetime],
        jump_channel_id: Optional[str] = None,
        remind_type: Union[RemindType, int],
    ) -> Schedule:
        if isinstance(start_timestamp, datetime):
            start_timestamp = int(start_timestamp.timestamp() * 1000)

        if isinstance(end_timestamp, datetime):
            end_timestamp = int(end_timestamp.timestamp() * 1000)

        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("channels", channel_id, "schedules"),
            json={
                "schedule": exclude_none(
                    {
                        "name": name,
                        "description": description,
                        "start_timestamp": (
                            str(start_timestamp)
                            if start_timestamp is not None
                            else None
                        ),
                        "end_timestamp": (
                            str(end_timestamp) if end_timestamp is not None else None
                        ),
                        "jump_channel_id": jump_channel_id,
                        "remind_type": str(remind_type),
                    }
                )
            },
        )
        return type_validate_python(Schedule, await self._request(request))

    @API
    async def patch_schedule(
        self,
        *,
        channel_id: str,
        schedule_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_timestamp: Optional[Union[int, datetime]] = None,
        end_timestamp: Optional[Union[int, datetime]] = None,
        jump_channel_id: Optional[int] = None,
        remind_type: Optional[Union[RemindType, int]] = None,
    ) -> Schedule:
        if isinstance(start_timestamp, datetime):
            start_timestamp = int(start_timestamp.timestamp() * 1000)

        if isinstance(end_timestamp, datetime):
            end_timestamp = int(end_timestamp.timestamp() * 1000)

        request = Request(
            "PATCH",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "schedules", schedule_id
            ),
            json={
                "schedule": exclude_none(
                    {
                        "name": name,
                        "description": description,
                        "start_timestamp": (
                            str(start_timestamp)
                            if start_timestamp is not None
                            else None
                        ),
                        "end_timestamp": (
                            str(end_timestamp) if end_timestamp is not None else None
                        ),
                        "jump_channel_id": jump_channel_id,
                        "remind_type": (
                            str(remind_type) if remind_type is not None else None
                        ),
                    }
                )
            },
        )
        return type_validate_python(Schedule, await self._request(request))

    @API
    async def delete_schedule(self, *, channel_id: str, schedule_id: str) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "schedules", schedule_id
            ),
        )
        return await self._request(request)

    @API
    async def put_message_reaction(
        self, *, channel_id: str, message_id: str, type: Union[EmojiType, int], id: str
    ) -> None:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath(
                "channels",
                channel_id,
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
        self, *, channel_id: str, message_id: str, type: Union[EmojiType, int], id: str
    ) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "channels",
                channel_id,
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
        channel_id: str,
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
                channel_id,
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
        channel_id: str,
        audio_url: Optional[str] = None,
        text: Optional[str] = None,
        status: Union[AudioStatus, int],
    ) -> dict[Never, Never]:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("channels", channel_id, "audio"),
            json=AudioControl(audio_url=audio_url, text=text, status=status).dict(
                exclude_none=True
            ),
        )
        return await self._request(request)

    @API
    async def put_mic(self, *, channel_id: str) -> dict[Never, Never]:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath("channels", channel_id, "mic"),
        )
        return await self._request(request)

    @API
    async def delete_mic(self, *, channel_id: str) -> dict[Never, Never]:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath("channels", channel_id, "mic"),
        )
        return await self._request(request)

    # Forum API
    @API
    async def get_threads_list(self, *, channel_id: str) -> GetThreadsListReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("channels", channel_id, "threads"),
        )
        return type_validate_python(GetThreadsListReturn, await self._request(request))

    @API
    async def get_thread(self, *, channel_id: str, thread_id: str) -> GetThreadReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "threads", thread_id
            ),
        )
        return type_validate_python(GetThreadReturn, await self._request(request))

    @overload
    async def put_thread(
        self,
        *,
        channel_id: str,
        title: str,
        content: str,
        format: Literal[1, 2, 3],
    ) -> PutThreadReturn: ...

    @overload
    async def put_thread(
        self,
        *,
        channel_id: str,
        title: str,
        content: RichText,
        format: Literal[4],
    ) -> PutThreadReturn: ...

    @API
    async def put_thread(
        self,
        *,
        channel_id: str,
        title: str,
        content: Union[str, RichText],
        format: Literal[1, 2, 3, 4],
    ) -> PutThreadReturn:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath("channels", channel_id, "threads"),
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
        return type_validate_python(PutThreadReturn, await self._request(request))

    @API
    async def delete_thread(self, *, channel_id: str, thread_id: str) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "channels", channel_id, "threads", thread_id
            ),
        )
        return await self._request(request)

    # API Permission API
    @API
    async def get_guild_api_permission(
        self, *, guild_id: str
    ) -> GetGuildAPIPermissionReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("guilds", guild_id, "api_permission"),
        )
        return type_validate_python(
            GetGuildAPIPermissionReturn, await self._request(request)
        )

    @API
    async def post_api_permission_demand(
        self,
        *,
        guild_id: str,
        channel_id: str,
        api_identify: APIPermissionDemandIdentify,
        desc: str,
    ) -> APIPermissionDemand:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath(
                "guilds", guild_id, "api_permission", "demand"
            ),
            json=exclude_none(
                {
                    "channel_id": channel_id,
                    "api_identify": api_identify.dict(exclude_none=True),
                    "desc": desc,
                }
            ),
        )
        return type_validate_python(APIPermissionDemand, await self._request(request))

    # WebSocket API
    @API
    async def url_get(self) -> UrlGetReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("gateway"),
        )
        return type_validate_python(UrlGetReturn, await self._request(request))

    @API
    async def shard_url_get(self) -> ShardUrlGetReturn:
        request = Request(
            "GET",
            self.adapter.get_api_base().joinpath("gateway", "bot"),
        )
        return type_validate_python(ShardUrlGetReturn, await self._request(request))

    # Interaction API
    @API
    async def put_interaction(
        self, *, interaction_id: str, code: Literal[0, 1, 2, 3, 4, 5]
    ) -> None:
        request = Request(
            "PUT",
            self.adapter.get_api_base().joinpath("interactions", interaction_id),
            json={"code": code},
        )
        return await self._request(request)

    # C2C API
    @API
    async def post_c2c_messages(
        self,
        *,
        openid: str,
        msg_type: Literal[0, 1, 2, 3, 4, 7],
        content: Optional[str] = None,
        markdown: Optional[MessageMarkdown] = None,
        keyboard: Optional[MessageKeyboard] = None,
        media: Optional[Media] = None,
        ark: Optional[MessageArk] = None,
        embed: Optional[MessageEmbed] = None,
        image: None = None,
        message_reference: None = None,
        stream: Optional[MessageStream] = None,
        prompt_keyboard: Optional[MessagePromptKeyboard] = None,
        action_button: Optional[MessageActionButton] = None,
        event_id: Optional[str] = None,
        msg_id: Optional[str] = None,
        msg_seq: Optional[int] = None,
        timestamp: Optional[Union[int, datetime]] = None,
    ) -> PostC2CMessagesReturn:
        # tmp fix. content must not be none if sending media
        # if media is not None and not content:
        #    content = " "

        if isinstance(timestamp, datetime):
            timestamp = int(timestamp.timestamp())
        elif timestamp is None:
            timestamp = int(datetime.now(timezone.utc).timestamp())

        json_data = exclude_none(
            {
                "msg_type": msg_type,
                "content": content,
                "markdown": (
                    markdown.dict(exclude_none=True) if markdown is not None else None
                ),
                "keyboard": (
                    keyboard.dict(exclude_none=True) if keyboard is not None else None
                ),
                "media": (media.dict(exclude_none=True) if media is not None else None),
                "ark": ark.dict(exclude_none=True) if ark is not None else None,
                "embed": (embed.dict(exclude_none=True) if embed is not None else None),
                "image": image,
                "message_reference": (
                    message_reference.dict(exclude_none=True)
                    if message_reference is not None
                    else None
                ),
                "stream": (
                    stream.dict(exclude_none=True, exclude_unset=True)
                    if stream is not None
                    else None
                ),
                "prompt_keyboard": (
                    prompt_keyboard.dict(exclude_none=True, exclude_unset=True)
                    if prompt_keyboard is not None
                    else None
                ),
                "action_button": (
                    action_button.dict(exclude_none=True)
                    if action_button is not None
                    else None
                ),
                "event_id": event_id,
                "msg_id": msg_id,
                "msg_seq": msg_seq,
                "timestamp": timestamp,
            }
        )
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("v2", "users", openid, "messages"),
            json=json_data,
        )
        return type_validate_python(PostC2CMessagesReturn, await self._request(request))

    @API
    async def post_c2c_files(
        self,
        *,
        openid: str,
        file_type: Literal[1, 2, 3, 4],
        url: Optional[str] = None,
        srv_send_msg: bool = True,
        file_data: Optional[Union[str, bytes]] = None,
    ) -> PostC2CFilesReturn:
        if isinstance(file_data, bytes):
            file_data = b64encode(file_data).decode()
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("v2", "users", openid, "files"),
            json=exclude_none(
                {
                    "file_type": file_type,
                    "url": url,
                    "srv_send_msg": srv_send_msg,
                    "file_data": file_data,
                }
            ),
        )
        return type_validate_python(PostC2CFilesReturn, await self._request(request))

    @API
    async def delete_c2c_message(self, *, openid: str, message_id: str) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "v2", "users", openid, "messages", message_id
            ),
        )
        return await self._request(request)

    # Group API
    @API
    async def post_group_messages(
        self,
        *,
        group_openid: str,
        msg_type: Literal[0, 1, 2, 3, 4, 7],
        content: Optional[str] = None,
        markdown: Optional[MessageMarkdown] = None,
        keyboard: Optional[MessageKeyboard] = None,
        media: Optional[Media] = None,
        ark: Optional[MessageArk] = None,
        embed: Optional[MessageEmbed] = None,
        image: None = None,
        message_reference: None = None,
        event_id: Optional[str] = None,
        msg_id: Optional[str] = None,
        msg_seq: Optional[int] = None,
        timestamp: Optional[Union[int, datetime]] = None,
    ) -> PostGroupMessagesReturn:
        # tmp fix. content must not be none if sending media
        # if media is not None and not content:
        #    content = " "

        if isinstance(timestamp, datetime):
            timestamp = int(timestamp.timestamp())
        elif timestamp is None:
            timestamp = int(datetime.now(timezone.utc).timestamp())

        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath(
                "v2", "groups", group_openid, "messages"
            ),
            json=exclude_none(
                {
                    "msg_type": msg_type,
                    "content": content,
                    "markdown": (
                        markdown.dict(exclude_none=True)
                        if markdown is not None
                        else None
                    ),
                    "keyboard": (
                        keyboard.dict(exclude_none=True)
                        if keyboard is not None
                        else None
                    ),
                    "media": (
                        media.dict(exclude_none=True) if media is not None else None
                    ),
                    "ark": ark.dict(exclude_none=True) if ark is not None else None,
                    "embed": (
                        embed.dict(exclude_none=True) if embed is not None else None
                    ),
                    "image": image,
                    "message_reference": (
                        message_reference.dict(exclude_none=True)
                        if message_reference is not None
                        else None
                    ),
                    "event_id": event_id,
                    "msg_id": msg_id,
                    "msg_seq": msg_seq,
                    "timestamp": timestamp,
                }
            ),
        )
        return type_validate_python(
            PostGroupMessagesReturn, await self._request(request)
        )

    @API
    async def post_group_files(
        self,
        *,
        group_openid: str,
        file_type: Literal[1, 2, 3, 4],
        url: Optional[str] = None,
        srv_send_msg: bool = True,
        file_data: Optional[Union[str, bytes]] = None,
    ) -> PostGroupFilesReturn:
        if isinstance(file_data, bytes):
            file_data = b64encode(file_data).decode()
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("v2", "groups", group_openid, "files"),
            json=exclude_none(
                {
                    "file_type": file_type,
                    "url": url,
                    "srv_send_msg": srv_send_msg,
                    "file_data": file_data,
                }
            ),
        )
        return type_validate_python(PostGroupFilesReturn, await self._request(request))

    @API
    async def delete_group_message(self, *, group_openid: str, message_id: str) -> None:
        request = Request(
            "DELETE",
            self.adapter.get_api_base().joinpath(
                "v2", "groups", group_openid, "messages", message_id
            ),
        )
        return await self._request(request)

    @API
    async def post_group_members(
        self,
        *,
        group_id: str,
        limit: Optional[int] = None,
        start_index: Optional[int] = None,
    ) -> PostGroupMembersReturn:
        request = Request(
            "POST",
            self.adapter.get_api_base().joinpath("v2", "groups", group_id, "members"),
            json=exclude_none({"limit": limit, "start_index": start_index}),
        )
        return type_validate_python(
            PostGroupMembersReturn, await self._request(request)
        )
