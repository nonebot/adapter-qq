from typing import TYPE_CHECKING, List, Union, Literal, Optional

from .model import *

if TYPE_CHECKING:

    class ApiClient:
        async def get_guild(self, *, guild_id: int) -> Guild: ...

        async def me(self) -> User: ...

        async def guilds(
            self,
            *,
            before: Optional[str] = ...,
            after: Optional[str] = ...,
            limit: Optional[float] = ...,
        ) -> List[Guild]: ...

        async def get_channels(self, *, guild_id: int) -> List[Channel]: ...

        async def post_channels(
            self,
            *,
            guild_id: int,
            name: str = ...,
            type: int = ...,
            sub_type: int = ...,
            position: Optional[int] = ...,
            parent_id: Optional[int] = ...,
            private_type: Optional[int] = ...,
            private_user_ids: Optional[List[int]] = ...,
        ) -> List[Channel]: ...

        async def get_channel(self, *, channel_id: int) -> Channel: ...

        async def patch_channel(
            self,
            *,
            channel_id: int,
            name: Optional[str] = ...,
            type: Optional[int] = ...,
            sub_type: Optional[int] = ...,
            position: Optional[int] = ...,
            parent_id: Optional[int] = ...,
            private_type: Optional[int] = ...,
        ) -> Channel: ...

        async def delete_channel(self, *, channel_id: int) -> None: ...

        async def get_members(
            self,
            *,
            guild_id: int,
            after: Optional[str] = ...,
            limit: Optional[float] = ...,
        ) -> List[Member]: ...

        async def get_member(self, *, guild_id: int, user_id: int) -> Member: ...

        async def delete_member(
            self,
            *,
            guild_id: int,
            user_id: int,
            add_blacklist: Optional[bool] = ...,
            delete_history_msg_days: Optional[Literal[-1, 0, 3, 7, 15, 30]] = ...,
        ) -> None: ...

        async def get_guild_roles(self, *, guild_id: int) -> GetGuildRolesReturn: ...

        async def post_guild_role(
            self,
            *,
            guild_id: int,
            name: str = ...,
            color: Optional[float] = ...,
            hoist: Optional[float] = ...,
        ) -> PostGuildRoleReturn: ...

        async def patch_guild_role(
            self,
            *,
            guild_id: int,
            role_id: int,
            name: Optional[str] = ...,
            color: Optional[float] = ...,
            hoist: Optional[float] = ...,
        ) -> PatchGuildRoleReturn: ...

        async def delete_guild_role(self, *, guild_id: int, role_id: int) -> None: ...

        async def put_guild_member_role(
            self, *, guild_id: int, role_id: int, user_id: int, id: Optional[str] = ...
        ) -> None: ...

        async def delete_guild_member_role(
            self, *, guild_id: int, role_id: int, user_id: int, id: Optional[str] = ...
        ) -> None: ...

        async def get_channel_permissions(
            self, *, channel_id: int, user_id: int
        ) -> ChannelPermissions: ...

        async def put_channel_permissions(
            self,
            *,
            channel_id: int,
            user_id: int,
            add: Optional[str] = ...,
            remove: Optional[str] = ...,
        ) -> None: ...

        async def get_channel_roles_permissions(
            self, *, channel_id: int, role_id: int
        ) -> ChannelPermissions: ...

        async def put_channel_roles_permissions(
            self,
            *,
            channel_id: int,
            role_id: int,
            add: Optional[str] = ...,
            remove: Optional[str] = ...,
        ) -> None: ...

        async def get_message_of_id(
            self, *, channel_id: int, message_id: str
        ) -> MessageGet: ...

        async def delete_message(
            self,
            *,
            channel_id: int,
            message_id: str,
            hidetip: bool = False,
        ) -> None: ...

        async def post_messages(
            self,
            *,
            channel_id: int,
            content: Optional[str] = ...,
            embed: Optional[MessageEmbed] = ...,
            ark: Optional[MessageArk] = ...,
            message_reference: Optional[MessageReference] = ...,
            image: Optional[str] = ...,
            file_image: Optional[bytes] = ...,
            markdown: Optional[MessageMarkdown] = ...,
            msg_id: Optional[str] = ...,
        ) -> Message: ...

        async def post_dms(
            self, *, recipient_id: str = ..., source_guild_id: str = ...
        ) -> DMS: ...

        async def post_dms_messages(
            self,
            *,
            guild_id: int,
            content: Optional[str] = ...,
            embed: Optional[MessageEmbed] = ...,
            ark: Optional[MessageArk] = ...,
            message_reference: Optional[MessageReference] = ...,
            image: Optional[str] = ...,
            file_image: Optional[bytes] = ...,
            markdown: Optional[MessageMarkdown] = ...,
            msg_id: Optional[str] = ...,
        ) -> Message: ...

        async def patch_guild_mute(
            self,
            *,
            guild_id: int,
            mute_end_timestamp: Optional[str] = ...,
            mute_seconds: Optional[str] = ...,
        ) -> None: ...

        async def patch_guild_member_mute(
            self,
            *,
            guild_id: int,
            user_id: int,
            mute_end_timestamp: Optional[str] = ...,
            mute_seconds: Optional[str] = ...,
        ) -> None: ...

        async def post_guild_announces(
            self, *, guild_id: int, message_id: str = ..., channel_id: str = ...
        ) -> None: ...

        async def delete_guild_announces(
            self, *, guild_id: int, message_id: str
        ) -> None: ...

        async def post_channel_announces(
            self, *, channel_id: int, message_id: str = ...
        ) -> Announces: ...

        async def delete_channel_announces(
            self, *, channel_id: int, message_id: str
        ) -> None: ...

        async def get_schedules(
            self, *, channel_id: int, since: Optional[int] = ...
        ) -> List[Schedule]: ...

        async def post_schedule(
            self,
            *,
            channel_id: int,
            name: str = ...,
            description: Optional[str] = ...,
            start_timestamp: int = ...,
            end_timestamp: int = ...,
            creator: Optional[Member] = ...,
            jump_channel_id: Optional[int] = ...,
            remind_type: str = ...,
        ) -> Schedule: ...

        async def get_schedule(
            self, *, channel_id: int, schedule_id: int
        ) -> Schedule: ...

        async def patch_schedule(
            self,
            *,
            channel_id: int,
            schedule_id: int,
            name: Optional[str] = ...,
            description: Optional[str] = ...,
            start_timestamp: Optional[int] = ...,
            end_timestamp: Optional[int] = ...,
            creator: Optional[Member] = ...,
            jump_channel_id: Optional[int] = ...,
            remind_type: Optional[str] = ...,
        ) -> Schedule: ...

        async def delete_schedule(
            self, *, channel_id: int, schedule_id: int
        ) -> None: ...

        async def audio_control(
            self,
            *,
            channel_id: int,
            audio_url: Optional[str] = ...,
            text: Optional[str] = ...,
            status: Optional[int] = ...,
        ) -> None: ...

        async def get_guild_api_permission(
            self, *, guild_id: int
        ) -> List[APIPermission]: ...

        async def post_api_permission_demand(
            self,
            *,
            guild_id: int,
            channel_id: Optional[str] = ...,
            api_identify: Optional[APIPermissionDemandIdentify] = ...,
            desc: Optional[str] = ...,
        ) -> List[APIPermissionDemand]: ...

        async def url_get(self) -> UrlGetReturn: ...

        async def shard_url_get(self) -> ShardUrlGetReturn: ...

        async def put_message_reaction(
            self, *, channel_id: int, message_id: str, type: int, id: str
        ) -> None: ...

        async def delete_own_message_reaction(
            self, *, channel_id: int, message_id: str, type: int, id: str
        ) -> None: ...

        async def put_pins_message(
            self, *, channel_id: int, message_id: str
        ) -> None: ...

        async def delete_pins_message(
            self, *, channel_id: int, message_id: str
        ) -> None: ...

        async def get_pins_message(self, *, channel_id: int) -> PinsMessage: ...

        async def get_threads_list(
            self, *, channel_id: int
        ) -> GetThreadsListReturn: ...

        async def get_thread(
            self, *, channel_id: int, thread_id: str
        ) -> GetThreadReturn: ...

        async def put_thread(
            self,
            *,
            channel_id: int,
            title: str,
            content: Union[str, RichText],
            format: PutThreadFormat,
        ) -> PutThreadReturn: ...

        async def delete_thread(self, *, channel_id: int, thread_id: str) -> None: ...

else:

    class ApiClient: ...
