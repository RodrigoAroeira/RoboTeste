from __future__ import annotations

import asyncio
import os
import socket
from datetime import datetime

import discord as dc
from discord.ext import commands
from discord.ext.commands import Context, command, hybrid_command, is_owner

START = datetime.fromtimestamp(
    float(os.environ.setdefault("START", str(datetime.now().astimezone().timestamp())))
)  # Persistant memory


async def setup(bot: commands.Bot):
    await bot.add_cog(Control(bot))


class Control(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start = START

    @hybrid_command(hidden=True)
    @is_owner()
    async def close(self, ctx: Context, seconds: int = 0):
        await ctx.send(f"Closing in {seconds}", ephemeral=True)
        ty = dc.ActivityType.watching
        for i in range(seconds):
            await asyncio.sleep(1)
            activity = dc.Activity(type=ty, name=f"{seconds - i}")
            await self.bot.change_presence(activity=activity)
        await self.bot.close()

    @command(hidden=True)
    @is_owner()
    async def commands(self, ctx: Context):
        commands = self.bot.commands
        ss = list(map(str, commands))
        await ctx.send(str(ss))

    @command(hidden=True)
    async def uptime(self, ctx: Context):
        now = datetime.now()
        delta = now - self.start

        total_seconds = int(delta.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if days > 0 or hours > 0:
            parts.append(f"{hours}h")
        if days > 0 or hours > 0 or minutes > 0:
            parts.append(f"{minutes}m")

        parts.append(f"{seconds}s")

        uptime_str = " ".join(parts)
        await ctx.send(f"Uptime: {uptime_str}")

    @command(hidden=True)
    @is_owner()
    async def where(self, ctx: Context):
        user = os.getlogin()
        host = socket.gethostname()

        await ctx.send(f"{user}@{host}")
