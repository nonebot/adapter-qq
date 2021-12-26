from pathlib import Path

import pytest


@pytest.fixture
def import_hook():
    import nonebot.adapters

    nonebot.adapters.__path__.append(  # type: ignore
        str((Path(__file__).parent.parent / "nonebot" / "adapters").resolve())
    )
