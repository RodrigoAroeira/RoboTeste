import asyncio
import os

import discord
from discord.ext import commands

from utils import is_command


async def setup(bot: commands.Bot):
    await bot.add_cog(Cog(bot))


class Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def latency(self, ctx: commands.Context):
        await ctx.send(f"Latency: {self.bot.latency}ms")

    @commands.hybrid_command()
    async def oi(self, ctx: commands.Context):
        name = ctx.author.display_name
        try:
            if (nick := ctx.author.nick) is not None:  # type:ignore
                name = nick
        except AttributeError:
            pass
        await ctx.send(content=f"Oi, {name}")

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send(content="Pong!")

    @commands.command(hidden=True, aliases=["cpf"])
    @commands.is_owner()
    async def leak(self, ctx: commands.Context):
        cpf = os.getenv("CPF")
        if not cpf:
            return
        msg = await ctx.send(cpf)
        await msg.delete()
        await ctx.message.delete()

    @commands.command(name="as")
    async def As(
        self, ctx: commands.Context, user: discord.User, command: str, *args: str
    ):
        if not command.strip():
            command = "oi"
        ctx.author = user
        msg = ctx.message
        msg.author = user
        msg.content = f"%{command} " + " ".join(map(str, args))
        await self.bot.on_message(msg)

    @commands.command()
    async def send(self, ctx: commands.Context, user: discord.User, *msg: str):
        """Envia mensagem a um outro usuário pelo bot"""
        name = ctx.author.display_name or ctx.author.name
        url = ctx.author.mention
        content = f"{name} ({url}) sent: " + " ".join(msg)
        await user.send(content=content)

    @commands.command(name="for")
    async def For(self, ctx: commands.Context, n: int, *contents: str):
        if not contents:
            return
        command_name = contents[0].lstrip("%")
        if not is_command(command_name, self):
            return
        msg = "%" + " ".join(contents)
        dc_msg = ctx.message
        dc_msg.content = msg
        for _ in range(n):
            await self.bot.on_message(dc_msg)
            await asyncio.sleep(0.5)
