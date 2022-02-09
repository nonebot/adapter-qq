from pathlib import Path

import httpx

from .config import Config


def get_source(config: Config) -> str:
    if isinstance(config.input, str):
        with open(config.input, "r", encoding="utf-8") as f:
            return f.read()
    elif isinstance(config.input, Path):
        with config.input.open("r", encoding="utf-8") as f:
            return f.read()
    elif config.url:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(config.url.geturl())
            if response.status_code != 200:
                raise Exception(f"Failed to get OpenAPI: {response.status_code}")
            return response.text

    raise ValueError(f"Failed to get OpenAPI")
