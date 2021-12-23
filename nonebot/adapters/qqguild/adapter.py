from typing import Any

from nonebot.drivers import Driver
from nonebot.typing import overrides

from nonebot.adapters import Adapter as BaseAdapter

from .config import Config


class Adapter(BaseAdapter):
    @overrides(BaseAdapter)
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        self.onebot_config: Config = Config(**self.config.dict())

    @classmethod
    @overrides(BaseAdapter)
    def get_name(cls) -> str:
        return "QQ Guild"
