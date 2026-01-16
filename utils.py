import os
from pathlib import Path
from typing import Generator, Iterable

from discord.ext import commands

from platformdirs import user_data_dir

DATA_DIR = Path(user_data_dir("robo-discord"))


def gather_cogs(path: Path | str = Path()) -> Generator[str]:
    for entry in Path(path).rglob("*.py"):
        if any(part.startswith(".") or "venv" in part for part in entry.parts):
            continue

        if "cog" in entry.name.lower():
            yield ".".join(entry.with_suffix("").parts)


def gather_owners() -> Generator[int]:
    for key, value in os.environ.items():
        if "OWNER_ID" in key:
            yield int(value)


def is_command(s: str, bot: commands.Bot) -> bool:
    return any(s == str(c) or c in c.aliases for c in bot.commands)


def create_path(path: Path | str, *, create_file: bool = True):
    for par in Path(path).parents:
        par.mkdir(parents=True, exist_ok=True)
    if create_file:
        with open(path, "a"):
            """Make sure file exists"""


class SizedList[T](list[T]):
    def __init__(self, size: int):
        if size <= 0:
            raise ValueError("Size for SizedList must be greater than 0")
        self.size = size
        super().__init__()

    def limit_size(self):
        while len(self) > self.size:
            del self[0]

    def append(self, item: T):
        super().append(item)
        self.limit_size()

    def extend(self, iterable: Iterable[T], /) -> None:
        super().extend(iterable)
        self.limit_size()
