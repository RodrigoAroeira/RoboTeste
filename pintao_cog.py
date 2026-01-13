from __future__ import annotations

import asyncio
import csv
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import DefaultDict

from discord import Embed, User
from discord.ext.commands import (
    BadArgument,
    Bot,
    Cog,
    Context,
    command,
    hybrid_command,
    parameter,
)
from platformdirs import user_data_dir

DATA_DIR = Path(user_data_dir("robo-discord"))

DATABASE_PATH = DATA_DIR / "pintao.json"
BEBIDAS_PATH = DATA_DIR / "bebidas.csv"


# TODO: Usar link encurtado ou outro link
URL_PINTAO = "https://cdn.discordapp.com/attachments/1204521622204325890/1458630896390377503/5d75e648-66a4-4b3b-b2e7-718bbb38adcb.png?ex=69605761&is=695f05e1&hm=44b4c82a9e851e492154624e7b17ed7599cb199d354d63fa33e3661a5e766414&"


async def setup(bot: Bot):
    await bot.add_cog(Pintao(bot))


class Pintao(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = Leaderboard(DATABASE_PATH)
        self.bebidas = BebidasCSV(BEBIDAS_PATH)

    async def cog_unload(self) -> None:
        await self.db.save()
        await self.bebidas.save()

    @hybrid_command()
    async def beber(
        self,
        ctx: Context,
        tipo: str = parameter(description="Tipo da bebida consumida"),
        quantidade: int = parameter(description="Unidades consumidas", default=1),
    ):
        """Adiciona no seu placar a bebida fornecida
        Exemplos:
            %beber beats
            %beber cerveja 3
            %beber beats 2
        """
        when = ctx.message.created_at.astimezone()
        _ = when.strftime("%d %b %Y, %H:%M")

        bebida = self.bebidas.get_bebida(tipo)
        for _ in range(quantidade):
            await self.db.adicionar(ctx.author.id, bebida)

        await ctx.send(
            f"Você adicionou {truncate(bebida.quant_alc * quantidade)} ao seu placar"
        )

    @command()
    async def vomitar(
        self,
        ctx: Context,
        tipo: str = parameter(description="Tipo da bebida consumida"),
        quantidade: int = parameter(description="Unidades consumidas", default=1),
    ):
        """Remove a bebida do placar"""
        if quantidade <= 0:
            raise BadArgument("quantidade deve ser um número inteiro positivo")

        when = ctx.message.created_at.astimezone()
        _ = when.strftime("%d %b %Y, %H:%M")

        bebida = self.bebidas.get_bebida(tipo)
        if bebida is None:
            raise BadArgument(f"'{tipo}' não é uma bebida válida")

        await self.db.remover(ctx.author.id, bebida, quantidade)

        await ctx.send(
            f"Você vomitou {truncate(bebida.quant_alc * quantidade)} de alcool"
        )

    # TODO: Remover codigo repetido
    @hybrid_command()
    async def pintao(
        self,
        ctx: Context,
        user: User | None = parameter(
            description="Usuário para checar posição no leaderboard. Opcional",
            default=None,
        ),
    ):
        """Mostra o placar da copa pintão"""
        embed = Embed(title="🍺 Pintão Leaderboard")
        embed.set_image(url=URL_PINTAO)

        def add_field(
            rank: int,
            user: User,
            alc: float,
            *,
            medal: str | None = None,
            inline: bool = False,
        ):
            if medal is None:
                medal = ""
            embed.add_field(
                name=f"#{rank} - {user.display_name}{medal}",
                value=truncate(alc),
                inline=inline,
            )

        ordered = sorted(self.db.data.items(), key=lambda tup: tup[1], reverse=True)
        medals = (":medal:", ":second_place:", ":third_place:")

        # --------------------- Caso usuario especifico ---------------------
        if user is not None:
            for i, (id, alc) in enumerate(ordered, start=1):
                if id == user.id:
                    add_field(i, user, alc)
                    await ctx.send(embed=embed)
                    return
            await ctx.send(f"{user.name} não encontrado no leaderboard")
            return

        # --------------------- Caso leaderboard geral ---------------------
        for i, (id, alc) in enumerate(ordered[:3]):
            medal = medals[i]
            rank1 = i + 1
            user = self.bot.get_user(id) or await self.bot.fetch_user(id)
            j = i + 3
            if j < len(ordered):
                rank2 = j + 1
                id2, alc2 = ordered[j]
                user2 = self.bot.get_user(id2) or await self.bot.fetch_user(id2)
                add_field(rank1, user, alc, inline=True, medal=medal)
                add_field(rank2, user2, alc2, inline=True, medal=None)
            else:
                add_field(rank1, user, alc, medal=medal)

        total = sum(alc for _, alc in ordered)
        embed.add_field(name="Total", value=truncate(total), inline=True)

        meta = 1000 * 269 * 0.079  # ml
        embed.add_field(name="Meta", value=truncate(meta) + "(1000 beats)", inline=True)
        await ctx.send(embed=embed)

    @hybrid_command(aliases=["cb"])
    async def cadastrar_bebida(
        self,
        ctx: Context,
        nome: str = parameter(description="Nome da bebida"),
        volume: float = parameter(description="Volume da bebida em mL"),
        abv: float = parameter(
            description="Conteúdo alcoólico da bebida. Números de 0 a 1"
        ),
        update: bool = parameter(
            description="Marca se a bebida será atualizada, caso já exista",
            default=False,
        ),
    ):
        """Cadastra uma nova bebida no registro de bebidas. Adicionar bebidas em quantidades bebíveis
        Exemplo: %cadastrar_bebida ice 750 0.05
        """
        nome = nome.capitalize()
        for c in nome:
            if not c.isalnum():
                raise BadArgument(f"Caractere proibido encontrado no nome: {c}")

        if not 0.0 <= volume <= 1000.0:
            raise BadArgument("Conteúdo deve ser entre 0 e 1000mL")
        if not 0.0 <= abv <= 1.0:
            raise BadArgument("ABV deve ser entre 0 e 1")

        await self.bebidas.adicionar_bebida(nome, volume, abv, update=update)
        await ctx.send(f"{nome} adicionado nas bebidas")

    @hybrid_command(aliases=["db"])
    async def descadastrar_bebida(
        self, ctx: Context, nome: str = parameter(description="Nome da bebida")
    ):
        """Cadastra uma nova bebida no registro de bebidas. Adicionar bebidas em quantidades bebíveis"""
        self.bebidas.remover_bebida(nome)
        await ctx.send(f"Bebida '{nome}' foi removida com sucesso")

    @command(name="bebidas")
    async def show_bebidas(self, ctx: Context):
        """Mostra a lista de bebidas existentes"""
        embed = Embed(title="Bebidas")
        embed.set_image(url=URL_PINTAO)
        for b in self.bebidas:
            value = f"Vol: {truncate(b.volume)}; ABV: {b.abv}"
            embed.add_field(name=b.nome, value=value, inline=False)
        await ctx.send(embed=embed)


def truncate(val: float) -> str:
    if val >= 1000:
        return f"{val / 1000:.3f}L"
    return f"{val:.3f}mL"


class Saveable(ABC):
    semaforo: asyncio.Semaphore

    @abstractmethod
    async def save(self): ...


@dataclass
class Leaderboard(Saveable):
    path: Path
    data: DefaultDict[int, float] = field(
        init=False, default_factory=lambda: DefaultDict(float)
    )
    semaforo: asyncio.Semaphore = field(init=False, default_factory=asyncio.Semaphore)

    async def save(self) -> None:
        async with self.semaforo:
            if not self.data:
                return

            existing = self.__load()
            if len(existing) > len(self.data):
                # There is more data in the file than in memory. Prevents loss
                return
            with open(self.path, "w") as f:
                json.dump(dict(self.data), f)
            print(f"Saved database: {self.path}")

    def __setup(self):
        for par in self.path.parents:
            par.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a"):
            """Simply make sure file exists"""

    def __load(self) -> DefaultDict[int, float]:
        with open(self.path) as f:
            content = f.read()
        if not content:
            return DefaultDict(float)
        obj = {int(id): n for id, n in json.loads(content).items()}
        return DefaultDict(float, obj)  # type: ignore

    def __post_init__(self):
        self.__setup()
        self.data = self.__load()

    async def __helper(
        self, user_id: int, tipo: Bebida, quantidade: int, *, remover: bool
    ):
        amount = tipo.quant_alc * quantidade
        if remover:
            self.data[user_id] -= amount
            if self.data[user_id] < 0:
                self.data[user_id] = 0
        else:
            self.data[user_id] += amount
        await self.save()

    async def adicionar(self, user_id: int, tipo: Bebida, quantidade: int):
        await self.__helper(user_id, tipo, quantidade, remover=False)

    async def remover(self, user_id: int, tipo: Bebida, quantidade: int):
        await self.__helper(user_id, tipo, quantidade, remover=True)


@dataclass
class BebidasCSV(Saveable):
    path: Path | str
    bebidas: list[Bebida] = field(init=False, default_factory=list)
    semaforo: asyncio.Semaphore = field(init=False, default_factory=asyncio.Semaphore)

    def __post_init__(self):
        with open(self.path, "a"):
            pass
        self.bebidas = self.__ler_csv_bebidas(self.path)

    async def save(self):
        async with self.semaforo:
            if not self.bebidas:
                return

            with open(self.path, "w") as f:
                w = csv.DictWriter(f, fieldnames=["bebida", "volume", "abv"])
                w.writeheader()
                for bebida in self.bebidas:
                    w.writerow(
                        {
                            "bebida": bebida.nome,
                            "volume": bebida.volume,
                            "abv": bebida.abv,
                        }
                    )

    async def adicionar_bebida(
        self, nome: str, volume: float, abv: float, *, update: bool = False
    ):
        if not update and self.get_bebida(nome) is not None:
            raise ValueError("Bebida já existe")
        bebida = Bebida(nome, volume, abv)
        self.bebidas.append(bebida)
        await self.save()

    def remover_bebida(self, nome: str):
        for b in self:
            if b.nome.lower() == nome.lower():
                self.bebidas.remove(b)
                return
        raise ValueError(f"Bebida {nome} não existe")

    def get_bebida(self, nome: str) -> Bebida | None:
        for b in self:
            if b.nome.lower() == nome.lower():
                return b
        return None

    def __ler_csv_bebidas(self, path: Path | str):
        bebidas = []

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                bebida = Bebida(
                    nome=row["bebida"],
                    volume=float(row["volume"]),
                    abv=float(row["abv"]),
                )
                bebidas.append(bebida)

        return bebidas

    def __iter__(self):
        yield from self.bebidas


@dataclass
class Bebida:
    nome: str
    volume: float
    abv: float

    def __validate__(self):
        if self.volume <= 0 or self.volume > 1000:
            raise ValueError("Volume deve estar entre 0 e 1000 mL.")
        if not 0 <= self.abv <= 1:
            raise ValueError("ABV deve estar entre 0 e 1.")

    def __post_init__(self):
        self.__validate__()

    @property
    def quant_alc(self) -> float:
        return self.volume * self.abv
