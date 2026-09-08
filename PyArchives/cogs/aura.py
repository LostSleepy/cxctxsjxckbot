"""Aura system cog: daily aura, leaderboard, Black Flash, admin tools."""

from __future__ import annotations

import logging
import random

import discord
from config import AURA_DATA_PATH, CANAL_ANUNCIOS_ID
from core.checks import admin_bypass_cooldown, is_admin
from core.embeds import error
from discord.ext import commands
from utils.aura_manager import AuraManager
from utils.gif_manager import get_aura_gif, get_giphy_gif

log = logging.getLogger(__name__)

MENSAJES_BF_RECORD: list[str] = [
    "⚡⚡⚡ **RÉCORD DE DESTELLOS NEGROS** ⚡⚡⚡\n"
    "{mention} ha encadenado Destellos consecutivos. "
    "Aura **duplicada** a **{aura} pts**. Histórico.",
    "⚡ **DESTELLO NEGRO PERFECTO** ⚡\n"
    "{mention} ha rozado lo imposible. Su aura explota hasta **{aura} pts**.",
    "💥 **CONVERGENCIA DE ENERGÍA MALDITA** 💥\n"
    "{mention} lo ha hecho. Aura **x2** — ahora en **{aura} pts**. "
    "El server tiembla.",
]


class Aura(commands.Cog):
    """Daily aura scores, leaderboard and Black Flash."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.aura_manager = AuraManager(AURA_DATA_PATH)

    # -- aura -------------------------------------------------------------
    @commands.command(name="aura")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def aura(self, ctx: commands.Context, miembro: discord.Member | None = None) -> None:
        """Consulta tu aura del día (se resetea cada 24h)."""
        await admin_bypass_cooldown(ctx)
        miembro = miembro or ctx.author
        puntos = await self.aura_manager.get_aura(str(miembro.id))
        embed = discord.Embed(
            title=f"✨ Aura de {miembro.display_name}",
            description=self.aura_manager.get_aura_message(puntos),
            color=discord.Color.gold() if puntos >= 0 else discord.Color.dark_red(),
        )
        embed.set_image(url=await get_aura_gif(puntos))
        embed.set_footer(text="Se resetea cada 24h.")
        await ctx.send(embed=embed)

    @commands.command(name="top", aliases=["ranking", "leaderboard"])
    async def top_aura(self, ctx: commands.Context) -> None:
        """Top 10 de aura del servidor."""
        await admin_bypass_cooldown(ctx)
        if ctx.guild is None:
            await ctx.send(
                embed=error("❌ Sin servidor", "Este comando solo funciona en un servidor.")
            )
            return
        guild_member_ids = {str(m.id) for m in ctx.guild.members if not m.bot}
        ranking = await self.aura_manager.get_top_aura(guild_member_ids, limit=10)
        if not ranking:
            await ctx.send("📊 Nadie ha consultado su aura hoy todavía.")
            return
        medallas = ["🥇", "🥈", "🥉"] + ["🔹"] * 7
        lineas: list[str] = []
        for i, (uid, puntos) in enumerate(ranking):
            miembro = ctx.guild.get_member(int(uid))
            nombre = miembro.display_name if miembro else f"ID {uid}"
            lineas.append(f"{medallas[i]} **{nombre}** — `{puntos} pts`")
        embed = discord.Embed(
            title="📊 Top Aura del servidor",
            description="\n".join(lineas),
            color=discord.Color.gold(),
        )
        embed.set_footer(text="Solo cuenta el aura de hoy.")
        await ctx.send(embed=embed)

    @commands.command(name="bf", aliases=["blackflash"])
    async def bf_command(
        self, ctx: commands.Context, usuario: discord.Member | None = None
    ) -> None:
        """Black Flash: 5% de probabilidad de duplicar tu aura."""
        if usuario is None:
            await ctx.send("❌ Debes mencionar a alguien para darle un Black Flash.")
            return
        if self.bot.user is not None and usuario.id == self.bot.user.id:
            await ctx.send("❌ No me metas a mí en esto.")
            return
        if usuario.id == ctx.author.id:
            await ctx.send("❌ No puedes usarlo contra ti mismo.")
            return
        if usuario.bot:
            await ctx.send("❌ Los bots no tienen aura que golpear.")
            return

        async with ctx.typing():
            gif = await get_giphy_gif("black flash")
            embed = discord.Embed(
                title="⚡¡Black Flash!⚡",
                description=(
                    f"{ctx.author.mention} le ha propinado un "
                    f"**Destello Negro** a {usuario.mention}."
                ),
                color=discord.Color.red(),
            )
            embed.set_image(url=gif)
            await ctx.send(embed=embed)

        if random.random() < 0.05:
            uid = str(ctx.author.id)
            existing = await self.aura_manager.get_aura_if_exists(uid)
            nueva = existing * 2 if existing is not None else 100
            await self.aura_manager.set_aura(uid, nueva)
            if CANAL_ANUNCIOS_ID and ctx.guild is not None:
                canal = self.bot.get_channel(CANAL_ANUNCIOS_ID)
                if canal is not None:
                    try:
                        mensaje = random.choice(MENSAJES_BF_RECORD).format(
                            mention=ctx.author.mention, aura=nueva
                        )
                        await canal.send(mensaje)
                    except discord.DiscordException:
                        pass

    # -- admin ------------------------------------------------------------
    @commands.command(name="setaura")
    @is_admin()
    async def set_aura_cmd(
        self, ctx: commands.Context, miembro: discord.Member | None = None, valor: int | None = None
    ) -> None:
        """[Admin] Fija el aura de un usuario. Uso: `cx!setaura @usuario [valor]`"""
        if miembro is None or valor is None:
            await ctx.send("Uso: `cx!setaura @usuario [valor]`")
            return
        if not -100_000 <= valor <= 100_000:
            await ctx.send("❌ El valor debe estar entre -100000 y 100000.")
            return
        await self.aura_manager.set_aura(str(miembro.id), valor)
        await ctx.send(f"✅ Aura de {miembro.mention} establecida a **{valor} pts**.")

    @commands.command(name="resetaura")
    @is_admin()
    async def reset_aura_cmd(
        self, ctx: commands.Context, miembro: discord.Member | None = None
    ) -> None:
        """[Admin] Resetea el aura de un usuario."""
        if miembro is None:
            await ctx.send("Uso: `cx!resetaura @usuario`")
            return
        await self.aura_manager.reset_aura(str(miembro.id))
        await ctx.send(f"✅ Aura de {miembro.mention} reseteada.")

    @commands.command(name="giveaura", aliases=["daraura", "regalaraura"])
    @is_admin()
    async def giveaura(
        self,
        ctx: commands.Context,
        usuario: discord.Member | None = None,
        cantidad: int | None = None,
    ) -> None:
        """[Admin] Suma (o resta) aura. Uso: `cx!giveaura @usuario <cantidad>`"""
        if usuario is None or cantidad is None:
            await ctx.send("❌ Usa: `cx!giveaura @usuario <cantidad>` (negativo para quitar)")
            return
        if not -100_000 <= cantidad <= 100_000:
            await ctx.send("❌ La cantidad debe estar entre -100000 y 100000.")
            return
        new_aura = await self.aura_manager.modify_aura(str(usuario.id), cantidad)
        emoji = "➕" if cantidad >= 0 else "➖"
        embed = discord.Embed(
            title=f"{emoji} Aura ajustada",
            description=(
                f"**{usuario.mention}** recibió **{cantidad:+d}** pts de aura.\n"
                f"📊 Ahora tiene **{new_aura}** pts."
            ),
            color=discord.Color.green() if cantidad >= 0 else discord.Color.red(),
        )
        await ctx.send(embed=embed)

    # Backwards-compat alias used by userinfo (Utilidad cog).
    @property
    def aura_manager_alias(self):
        return self.aura_manager


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Aura(bot))
