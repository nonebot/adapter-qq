from datetime import datetime
from typing import List, Optional

from pydantic import Extra, BaseModel, root_validator

from .transformer import BoolToIntTransformer, ExcludeNoneTransformer


class Model(BaseModel, extra=Extra.allow):
    ...


# Guild API
class Guild(BoolToIntTransformer, Model):
    id: str
    name: str
    icon: Optional[str] = None
    owner_id: str
    owner: bool
    memeber_count: int
    max_members: int
    description: str
    joined_at: Optional[datetime] = None


# Guild Role API
class Role(BoolToIntTransformer, Model):
    id: str
    name: str
    color: int
    hoist: bool
    number: int
    memeber_limit: int


class GuildRoles(Model):
    guild_id: str
    roles: List[Role]
    role_num_limit: str


class RoleUpdateFilter(BoolToIntTransformer, Model):
    name: bool
    color: bool
    hoist: bool


class RoleUpdateInfo(BoolToIntTransformer, ExcludeNoneTransformer, Model):
    name: Optional[str] = None
    color: Optional[int] = None
    hoist: Optional[bool] = None

    @root_validator
    def check_field(cls, values):
        if any(map(lambda v: v is not None, values)):
            return values
        raise ValueError("At least one field must be specified.")


class CreateRole(Model):
    role_id: str
    role: Role


class PatchRole(Model):
    guild_id: str
    role_id: str
    role: Role


# User API
class User(Model):
    id: str
    username: str
    avatar: Optional[str] = None
    bot: bool
    union_openid: Optional[str] = None
    union_user_account: Optional[str] = None


# WebSocket API
class SessionStartLimit(Model):
    total: int
    remaining: int
    reset_after: int
    max_concurrency: int


class Gateway(Model):
    url: str


class GatewayWithShards(Gateway):
    shards: int
    session_start_limit: SessionStartLimit
