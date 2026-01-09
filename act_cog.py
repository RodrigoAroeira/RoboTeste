import asyncio
import random as rd
from pprint import pformat
from typing import Optional

import discord as dc
from discord import ActivityType as AT
from discord.ext.commands import Bot, Cog, Context, command, hybrid_command, is_owner

from utils import SizedList

CHANGE_SECONDS = 600


async def setup(bot: Bot):
    if bot.status in (dc.Status.offline, dc.Status.invisible):
        return
    await bot.add_cog(Activities(bot))


def fmt(a: AT) -> str:
    return str(a).split(".")[1].title()


# TODO: Change to file containing activities and activity type
activities: dict[str, list[AT]] = {
    "Góticas peidando": [AT.watching, AT.listening],
    "GTA: SA - Góticas Tesudas e Altonas: Sensações Adstringentes": [
        AT.playing,
        AT.competing,
        AT.watching,
    ],
    "Góticas me xingando ASMR": [AT.listening],
    "Góticas mineiras fazendo pão de queijo": [AT.watching],
    "Góticas góticas escrevendo poesia gótica sob a luz gótica da lua gótica": [
        AT.watching
    ],
    "Góticas explorando cemitérios à noite (podcast roleplay)": [AT.listening],
    "Simulador de gótica zumbi": [AT.playing],
    "Boku no piku (gótico)": [AT.watching],
    "24a partida da série B gótica": [AT.watching],
    "Aerials versão forró": [AT.listening],
    "A Ordem Paranormal": [AT.playing, AT.watching],
    "Você mijar": [AT.listening, AT.watching],
    "Curso de hipnose quântica": [AT.watching],
    "Curso de vampirismo quântico": [AT.watching, AT.competing],
    "Videoaula - Atualizando o javascript mental para 1.8 python": [AT.watching],
    "Góticas baianas comendo acarajé - mukbang": [AT.watching],
    "Góticas cariocas praticando latrocínio": [AT.watching],
    "Big Titty Goth Girlfriend": [AT.playing, AT.watching],
    "Copa Pintão": [AT.competing],
    "10 horas de silêncio quebrado por gemidão do zap": [AT.listening],
    "Bíblia chinesa": [AT.listening],
    "Sex With Hitler": [AT.playing],
    "Apostando até as calças": [AT.competing],
    "Tigrinho": [AT.playing],
}

activities_size = sum(len(lst) for lst in activities.values())
seen: SizedList[tuple[str, AT]] = SizedList(activities_size // 2)


def _choose_random(tup: tuple[str, list[AT]]) -> tuple[str, AT]:
    s, lst = tup
    val = rd.choice(lst)
    return s, val


def _get_status() -> tuple[str, AT]:
    lst = list(activities.items())
    while (pair := _choose_random(rd.choice(lst))) in seen:
        pass

    seen.append(pair)
    return pair


class Activities(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.remaining_seconds = CHANGE_SECONDS

    @Cog.listener()
    async def on_ready(self):
        await self.change_status()

    def reset_seconds(self):
        self.remaining_seconds = CHANGE_SECONDS

    async def new_status(self, ctx: Optional[Context] = None):
        title, status = _get_status()
        activity = dc.Activity(type=status, name=title)
        await self.bot.change_presence(activity=activity)
        if ctx:
            await ctx.send(f"Status mudado para {fmt(status)} {title}", ephemeral=True)

    async def change_status(self):
        while True:
            await self.new_status()
            while self.remaining_seconds > 0:
                await asyncio.sleep(1)
                self.remaining_seconds -= 1  # race conditions don't matter in this case
            self.reset_seconds()

    @hybrid_command(hidden=True)
    @is_owner()
    async def mudar(self, ctx: Context):
        await self.new_status(ctx)
        self.reset_seconds()

    @hybrid_command(hidden=True)
    @is_owner()
    async def actv_status(self, ctx: Context):
        buf = ""
        await ctx.defer(ephemeral=True)
        fmt_atv = pformat(
            {t: list(map(fmt, lst)) for t, lst in activities.items()}, indent=2
        )
        buf += f"max len\n`{activities_size // 2}`\n"

        buf += f"activities\n```\n{fmt_atv}\n```\n"

        fmt_seen = pformat([(name, fmt(status)) for name, status in seen], indent=2)

        buf += f"seen\n```\n{fmt_seen}\n```\n"

        buf += f"Duration Seconds\n```\n{CHANGE_SECONDS}s\n```\n"
        await ctx.send(buf)

    @command(hidden=True)
    async def to_change(self, ctx: Context):
        await ctx.send(f"{self.remaining_seconds}s until next status change")

    @command(hidden=True, aliases=["off"])
    @is_owner()
    async def offline(self, *_):
        await self.bot.change_presence(status=dc.Status.offline)
