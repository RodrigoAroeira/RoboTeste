#!/usr/bin/env -S uv run --script
from __future__ import annotations

import asyncio
import os

import discord as dc
from discord.ext import commands

from bot import MyBot
from utils import gather_cogs, gather_owners


def main():
    from dotenv import load_dotenv

    env_path = os.getenv("ENV", ".env")
    load_dotenv(env_path)

    intents = dc.Intents.all()
    status = dc.Status.online
    print(f"Starting {status}")
    bot = MyBot(
        command_prefix=commands.when_mentioned_or(os.getenv("PREFIX", "!")),
        intents=intents,
        status=status,
        owner_ids=list(gather_owners()),
    )

    asyncio.run(bot.load_extensions(gather_cogs()))
    TOKEN = os.environ["DISCORD_TOKEN"]
    bot.run(TOKEN)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Encountered an error:", e)
