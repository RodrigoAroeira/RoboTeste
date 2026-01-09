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
        if isinstance(err, commands.MissingRequiredArgument):
            await ctx.send("Missing required arguments.")
            await ctx.send_help(ctx.command)
        else:
            await ctx.send(f"Error when executing command: `{err}`")
            return await super().on_command_error(ctx, err)

    async def on_message(self, message: dc.Message) -> None:
        content = message.content

        author = message.author
        guild = message.guild
        guild_str = "Direct" if not guild else f"{guild.name}"
        channel = "" if not guild else f"/{message.channel.name}"  # type: ignore

        data = message.created_at.astimezone().strftime("%d %b %Y, %H:%M")
        bot_info = "(BOT)" if message.author.bot else ""
        log_msg = f"{guild_str}{channel} - {author}: {content}\n"
        print(f"LOG{bot_info} {data}: {log_msg}", end="")
        with open("/tmp/log.txt", "a") as f:
            f.write(log_msg)
        await super().on_message(message)
