import asyncio
import os

import discord
from discord.ext import commands


async def setup(bot):
    await bot.add_cog(Cog(bot))


def is_command(s: str, obj):
    try:
        return s in obj._commands
    except AttributeError:
        return False


def register_commands[C](cls: C) -> C:
    cls._commands = set()  # type:ignore
    for method in dir(cls):
        attr = getattr(cls, method)
        if isinstance(attr, commands.Command):
            cls._commands.add(str(attr))  # type: ignore
    return cls


@register_commands
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

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx: commands.Context):
        """Shuts down bot and restarts"""
        if self.bot.owner_ids is None:
            await ctx.send("Unable to verify permissions")
            return

        if ctx.author.id not in self.bot.owner_ids:
            await ctx.send("Only the owners are able to run this command")
            return

        await ctx.send(content="Functionality not yet implemented")

    @commands.hybrid_command()
    async def gif(self, ctx):
        url = "https://media.tenor.com/eR3p9ASRcnUAAAAM/jerma-screaming.gif"
        msg = await ctx.send(content=url)
        await msg.delete(delay=5)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def leak(self, ctx: commands.Context):
        cpf = os.getenv("CPF")
        if not cpf:
            return
        msg = await ctx.send(cpf)
        await msg.delete()
        await ctx.message.delete()

    @commands.hybrid_command(hidden=True)
    @commands.is_owner()
    async def close(self, ctx: commands.Context):
        await ctx.message.delete()
        await self.bot.close()

    @commands.command()
    async def test(self, ctx: commands.Context, a: str = "", *rest):
        await ctx.send(content=f"author = {ctx.author}, {a = }, {rest = }")

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
