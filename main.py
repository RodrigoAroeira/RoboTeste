#!/usr/bin/env -S uv run --script
import asyncio
import os
from typing import Iterable

import discord as dc
from discord.ext import commands

from utils import gather_cogs, gather_owners


class Bot(commands.Bot):
    async def load_extensions(self, files: Iterable[str]):
        for file in files:
            await self.load_extension(file)

    async def on_ready(self):
        guilds = [guild async for guild in self.fetch_guilds()]
        for guild in guilds:
            print(f"\t- Online em {guild.name}")
            usernicks = {}
            users = [u async for u in guild.fetch_members()]
            for user in users:
                if user.bot:
                    continue
                usernicks[user.name] = user.nick or user.display_name
            longestname = len(max(usernicks.keys(), key=lambda x: len(x)))
            for n in usernicks:
                print(f"\t\t{n: <{longestname}} - {usernicks[n]}")
        print("Status:", self.status)

    def check_if_owner(self, user: dc.User | dc.Member) -> bool:
        if not self.owner_ids:
            self.owner_ids = ()
        return user.id in self.owner_ids


def main():
    from dotenv import load_dotenv

    env_path = os.getenv("ENV", ".env")
    load_dotenv(env_path)

    intents = dc.Intents.all()
    status = dc.Status.online
    print(f"Starting {status}")
    bot = Bot(
        command_prefix=commands.when_mentioned_or(os.getenv("PREFIX", "!")),
        intents=intents,
        status=status,
        owner_ids=list(gather_owners()),
    )

    asyncio.run(bot.load_extensions(gather_cogs()))
    TOKEN = os.environ["DISCORD_TOKEN"]
    bot.run(TOKEN)


if __name__ == "__main__":
    raise SystemExit(main())
