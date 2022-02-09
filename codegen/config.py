from pathlib import Path
from typing import Any, Dict

import tomli
from black.files import find_pyproject_toml
from datamodel_code_generator.__main__ import Config as BaseConfig


class Config(BaseConfig):
    ...


def get_config() -> Config:
    pyproject_toml_path = find_pyproject_toml((str(Path().resolve()),))
    if not pyproject_toml_path:
        raise ValueError("No pyproject.toml found")
    pyproject_toml_path = Path(pyproject_toml_path)
    with pyproject_toml_path.open("r", encoding="utf-8") as f:
        pyproject_toml = tomli.loads(f.read())
        config = pyproject_toml.get("tool", {}).get("codegen", {})
        pyproject_toml: Dict[str, Any] = {
            k.replace("--", "").replace("-", "_"): v for k, v in config.items()
        }
        return Config.parse_obj(pyproject_toml)
