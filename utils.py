import os
from pathlib import Path
from typing import Generator


def gather_cogs(path: Path | str = Path()) -> Generator[str]:
    for file in Path(path).iterdir():
        if "cog" not in file.name:
            continue
        yield str(file).removesuffix(".py")


def gather_owners() -> Generator[int]:
    for key, value in os.environ.items():
        if "OWNER_ID" in key:
            yield int(value)
