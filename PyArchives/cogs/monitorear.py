"""
Voice monitoring cog for the Teto Discord bot.
Includes the Date Magnet system and Restraining Orders between users.
"""
import asyncio
import json
import logging
import random
from pathlib import Path
from typing import Optional, Set

import discord
from discord.ext import commands

from config import (
    CANAL_CITAS_ID,
    ORDENES_ALEJAMIENTO_PATH,
    USER_CITA_1,
    USER_CITA_2,
)

log = logging.getLogger(__name__)


def _cargar_ordenes(path: Path) -> Set[int]:
    """Load restraining order pairs from JSON file."""
    if not path.exists():
        return set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Convert list of tuples to set of frozensets for hashability
        return {frozenset((a, b)) for a, b in data}
    except (json.JSONDecodeError, OSError, ValueError):
        return set()


def _guardar_ordenes(ordenes: set, path: Path) -> None:
    """Save restraining order pairs to JSON file atomically."""
    data = [tuple(p) for p in ordenes]
    temp = path.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp.replace(path)


class Monitorear(commands.Cog):
    """
    Voice channel monitoring systems.
    - Date Magnet: moves configured users to the date channel when both are in voice.
    - Restraining Orders: separates two users if they end up in the same voice channel.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        # Date magnet config
        self._id_1: int = USER_CITA_1
        self._id_2: int = USER_CITA_2
        self._canal_citas_id: int = CANAL_CITAS_ID
        self._activo: bool = True

        # Restraining orders (persisted to JSON)
        self._ordenes_alejamiento: Set[frozenset] = _cargar_ordenes(
            ORDENES_ALEJAMIENTO_PATH
        )

    # ── Toggle Monitor ───────────────────────────────────────────────────────
    @commands.command(name="nxc")
    @commands.has_permissions(administrator=True)
    async def toggle_monitor(self, ctx: commands.Context) -> None:
        """Toggle the voice monitoring system on/off."""
        self._activo = not self._activo
        estado = "ACTIVADO" if self._activo else "DESACTIVADO"
        color = discord.Color.green() if self._activo else discord.Color.red()
        embed = discord.Embed(
            title="Sistema de Monitoreo",
            description=f"El imán de coexistencia ha sido **{estado}**.",
            color=color,
        )
        await ctx.send(embed=embed)
        log.info(
            "Monitoreo %s por %s",
            estado, ctx.author.display_name,
        )

    # ── Restraining Order ────────────────────────────────────────────────────
    @commands.command(name="oa", aliases=["ordenalejamiento"])
    @commands.has_permissions(administrator=True)
    async def orden_alejamiento(
        self,
        ctx: commands.Context,
        user1: Optional[discord.Member] = None,
        user2: Optional[discord.Member] = None,
    ) -> None:
        """
        Toggle a restraining order between two users.
        If active and they meet in a voice channel, user2 is moved away.
        """
        if user1 is None or user2 is None:
            await ctx.send(
                "❌ Menciona a los dos usuarios. Ej: `cx!oa @user1 @user2`"
            )
            return
        if user1.id == user2.id:
            await ctx.send(
                "❌ No puedes poner una orden entre la misma persona."
            )
            return

        par = frozenset({user1.id, user2.id})

        if par in self._ordenes_alejamiento:
            self._ordenes_alejamiento.discard(par)
            _guardar_ordenes(self._ordenes_alejamiento, ORDENES_ALEJAMIENTO_PATH)
            await ctx.send(
                f"✅ Orden de alejamiento entre {user1.mention} y "
                f"{user2.mention} **desactivada**."
            )
            log.info(
                "OA desactivada: %s — %s",
                user1.display_name, user2.display_name,
            )
        else:
            self._ordenes_alejamiento.add(par)
            _guardar_ordenes(self._ordenes_alejamiento, ORDENES_ALEJAMIENTO_PATH)
            await ctx.send(
                f"🚫 Orden de alejamiento activada entre {user1.mention} "
                f"y {user2.mention}. Si coinciden en voz, "
                f"{user2.mention} será movido automáticamente."
            )
            log.info(
                "OA activada: %s — %s",
                user1.display_name, user2.display_name,
            )

    # ── Voice State Listener ─────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        """
        Monitor voice state changes for:
        1. Date Magnet — move configured users to the date channel.
        2. Restraining Orders — separate users under a restraining order.
        """
        # Skip if leaving or no channel
        if after.channel is None:
            return

        guild = member.guild

        # ── 1. Date Magnet ───────────────────────────────────────────────────
        if self._activo and member.id in (self._id_1, self._id_2):
            m1 = guild.get_member(self._id_1)
            m2 = guild.get_member(self._id_2)
            canal_citas = self.bot.get_channel(self._canal_citas_id)

            if (
                m1 and m1.voice
                and m2 and m2.voice
                and canal_citas is not None
                and (
                    m1.voice.channel.id != self._canal_citas_id
                    or m2.voice.channel.id != self._canal_citas_id
                )
            ):
                try:
                    await asyncio.gather(
                        m1.move_to(canal_citas, reason="Coexistencia detectada."),
                        m2.move_to(canal_citas, reason="Coexistencia detectada."),
                    )
                    log.info(
                        "Imán de citas: %s y %s → %s",
                        m1.display_name, m2.display_name, canal_citas.name,
                    )
                except discord.DiscordException as e:
                    log.error("Error en imán de citas: %s", e)

        # ── 2. Restraining Orders ────────────────────────────────────────────
        if not self._ordenes_alejamiento:
            return

        # Check if this member is part of any active order
        for par in self._ordenes_alejamiento:
            if member.id not in par:
                continue
            otro_id = next(uid for uid in par if uid != member.id)
            otro = guild.get_member(otro_id)

            if (
                otro
                and otro.voice
                and otro.voice.channel == after.channel
            ):
                # Both are in the same channel — move the other member
                canales_disponibles = [
                    c for c in guild.voice_channels
                    if c.id != after.channel.id
                    and c.permissions_for(guild.me).move_members
                ]
                if canales_disponibles:
                    destino = random.choice(canales_disponibles)
                    try:
                        await otro.move_to(
                            destino,
                            reason="Orden de alejamiento activa.",
                        )
                        log.info(
                            "OA: %s movido de %s a %s",
                            otro.display_name,
                            after.channel.name,
                            destino.name,
                        )
                    except discord.DiscordException as e:
                        log.error("Error en OA: %s", e)
                break


async def setup(bot: commands.Bot) -> None:
    """Load the Monitorear cog."""
    await bot.add_cog(Monitorear(bot))
