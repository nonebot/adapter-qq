import warnings

from .event import *
from .permission import *
from .bot import Bot as Bot
from .utils import log as log
from .adapter import Adapter as Adapter
from .message import Message as Message
from .message import MessageSegment as MessageSegment

warnings.warn(
    'QQGuild adapter is deprecated. Please use "nonebot-adapter-qq" instead.',
    DeprecationWarning,
)
