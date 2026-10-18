from nonebot.compat import PYDANTIC_V2, type_validate_python
from pydantic import ValidationError
import pytest
from yarl import URL

from nonebot.adapters.qq.config import Config


def test_pydantic_version_matches_env():
    import pydantic

    assert PYDANTIC_V2 == pydantic.VERSION.startswith("2.")


def test_config_defaults():
    config = type_validate_python(Config, {})
    assert config.qq_custom_gateway_url is None
    assert config.qq_bots == []


def test_custom_gateway_url_from_str():
    config = type_validate_python(Config, {"qq_custom_gateway_url": "wss://a.b/c"})
    assert config.qq_custom_gateway_url == URL("wss://a.b/c")


def test_custom_gateway_url_from_url():
    url = URL("ws://localhost:8080/ws")
    config = type_validate_python(Config, {"qq_custom_gateway_url": url})
    assert config.qq_custom_gateway_url == url


@pytest.mark.parametrize("value", ["http://a.b/c", "wss://"])
def test_custom_gateway_url_invalid(value: str):
    with pytest.raises(ValidationError):
        type_validate_python(Config, {"qq_custom_gateway_url": value})
