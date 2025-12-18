import os
from typing import Iterable

import discord as dc
from discord.ext import commands


class MyBot(commands.Bot):
    async def load_extensions(self, files: Iterable[str]):
        for file in files:
            await self.load_extension(file)

    async def on_ready(self):
        await self.tree.sync()
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

    async def on_command_error(self, ctx: commands.Context, err: commands.CommandError):
        await ctx.send(f"Error when executing command: `{err}`")
        return await super().on_command_error(ctx, err)

    async def on_message(self, message: dc.Message) -> None:
        if self.status in (dc.Status.invisible, dc.Status.offline):
            return
        await super().on_message(message)
        content = message.content
        if not content.startswith(str(os.getenv("PREFIX"))):
            return
        author = message.author
        where = "Direct" if not message.guild else message.guild.name

        print(f"LOG: {where} - {author}: {content}")
