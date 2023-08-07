from pathlib import Path
from typing import Any, Dict

import tomli
from pydantic import BaseModel


class Config(BaseModel):
    url: str
    model_output: Path
    client_output: Path
    handle_output: Path

    class Config:
        arbitrary_types_allowed = True


def get_config(options: Dict[str, Any]) -> Config:
    pyproject_toml_path = Path("./pyproject.toml")
    if not pyproject_toml_path:
        raise ValueError("No pyproject.toml found")
    pyproject_toml = tomli.loads(pyproject_toml_path.read_text())
    config = pyproject_toml.get("tool", {}).get("codegen", {})
    pyproject_toml: Dict[str, Any] = {
        k.replace("--", "").replace("-", "_"): v for k, v in config.items()
    }
    pyproject_toml.update(options)
    return Config.parse_obj(pyproject_toml)
