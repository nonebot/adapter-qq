from pathlib import Path
from typing import Dict, ClassVar, Sequence, cast

import yaml
import httpx
from yarl import URL
from pydantic import BaseModel

from .model import DataType


class Source(BaseModel):
    source: URL
    data: DataType
    _cache: ClassVar[Dict[URL, "Source"]] = {}

    class Config:
        arbitrary_types_allowed = True

    def resolve(self, ref: URL) -> "Source":
        url = self.source.join(ref).with_fragment("")

        source = self._cache.get(url, self.from_source(url))
        return source

    @classmethod
    def from_source(cls, source: URL) -> "Source":
        source = source.with_fragment("")
        if source in cls._cache:
            return cls._cache[source]

        if source.scheme == "file":
            path = Path(source.path)
            data = yaml.safe_load(path.read_text())
            obj = cls(source=source, data=data)
            cls._cache[source] = obj
            return obj

        with httpx.Client(follow_redirects=True) as client:
            res = client.get(str(source))
            if res.status_code != 200:
                raise RuntimeError(f"Failed to get {source}")
            data = yaml.safe_load(res.text)
            obj = cls(source=source, data=data)
            cls._cache[source] = obj
            return obj

    def resolve_fragment(self, fragment: str) -> DataType:
        fragment = fragment.lstrip("/")

        if not fragment:
            return self.data

        # Resolve via path
        parts = fragment.split("/")
        _d: DataType = self.data
        for part in parts:
            part = part.replace("~1", "/").replace("~0", "~")

            if isinstance(_d, Sequence):
                # Array indexes should be turned into integers
                try:
                    part = int(part)
                except ValueError:
                    pass

            try:
                _d = cast(DataType, _d)[part]
            except Exception:
                raise ValueError(
                    f"Unresolvable JSON pointer: {fragment!r}",
                )

        return _d
