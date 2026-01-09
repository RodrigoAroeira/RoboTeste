from __future__ import annotations

from discord.ext import commands as cmds

from utils import gather_cogs


async def setup(bot: cmds.Bot):
    await bot.add_cog(ReloadCog(bot))


class ReloadCog(cmds.Cog):
    def __init__(self, bot: cmds.Bot):
        self.bot = bot

    @cmds.hybrid_command(hidden=True, aliases=["rld"])
    @cmds.is_owner()
    async def reload(self, ctx: cmds.Context):
        cogs = list(filter(lambda s: len(s), gather_cogs()))
        if not cogs:
            await ctx.send("No cogs found", ephemeral=True, silent=True)
            return
        for file in cogs:
            try:
                await self.bot.reload_extension(file)
            except cmds.ExtensionNotLoaded:
                await self.bot.load_extension(file)
                await ctx.send(f"Loaded new extension {file}", ephemeral=True)

        await ctx.send("Cogs reloaded", ephemeral=True)
        await self.bot.tree.sync(guild=ctx.guild)
        await self.run_onready()

    async def run_onready(self):
        for name in self.bot.cogs:
            cog = self.bot.get_cog(name)
            if cog is None:
                continue
            if hasattr(cog, "on_ready"):
                await cog.on_ready()  # type: ignore

    @cmds.command()
    async def cogs(self, ctx: cmds.Context):
        await ctx.send(f"Existing cogs: {tuple(gather_cogs())}")
        await ctx.send(f"Loaded cogs: {self.bot.cogs}")
