from __future__ import annotations
from typing import TYPE_CHECKING

from discord.ext import commands as cmds

from utils import gather_cogs

if TYPE_CHECKING:
    from main import Bot


async def setup(bot):
    await bot.add_cog(ReloadCog(bot))


class ReloadCog(cmds.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @cmds.hybrid_command(hidden=True, aliases=["rld"])
    async def reload_cogs(self, ctx: cmds.Context):
        if not self.bot.check_if_owner(ctx.author):
            await ctx.send("Only the owner is allowed to run this command")
            return

        for file in gather_cogs():
            if not file:
                continue
            # await ctx.send(f"Found {file}")
            await self.bot.reload_extension(file)
