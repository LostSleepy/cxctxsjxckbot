"""
Moderation commands cog for the Teto Discord bot.
Includes voice roulette, AngelGuard timeout remover, and message purge.
"""
import logging
import random
from typing import List

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class Moderacion(commands.Cog):
    """Server moderation commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── Russian Roulette (voice kick) ────────────────────────────────────────
    @commands.command(name="ruleta", aliases=["ruleta_rusa"])
    async def ruleta_rusa(self, ctx: commands.Context) -> None:
        """Randomly kick a member from your voice channel."""
        log.debug("Ruleta ejecutado por %s", ctx.author.name)

        if not ctx.author.voice:
            await ctx.send("❌ Error: No detecto que estés en un canal de voz.")
            return

        canal = ctx.author.voice.channel
        victimas: List[discord.Member] = [
            m for m in canal.members if not m.bot
        ]

        log.debug(
            "Canal: %s — Miembros: %d — Víctimas: %d",
            canal.name,
            len(canal.members),
            len(victimas),
        )

        if not victimas:
            await ctx.send(
                f"❌ No encontré víctimas humanas en `{canal.name}`. "
                "¿Tienes los Privileged Intents activos?"
            )
            return

        elegido = random.choice(victimas)
        await ctx.send(f"🎲 La ruleta gira... apuntando a {elegido.mention}")

        try:
            await elegido.move_to(None)
            await ctx.send(
                f"💥 {elegido.display_name} ha sido expulsado de la llamada."
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ No tengo permisos (Mover Miembros) para desconectar "
                "a esa persona."
            )
        except discord.DiscordException as e:
            await ctx.send(f"⚠️ Error inesperado: {e}")
            log.error("Error en ruleta: %s", e, exc_info=True)

    # ── AngelGuard (remove all timeouts) ─────────────────────────────────────
    @commands.command(name="angelguard")
    @commands.has_permissions(moderate_members=True)
    async def angelguard(self, ctx: commands.Context) -> None:
        """Remove all active timeouts on the server."""
        count = 0
        status_msg = await ctx.send(
            "😇 **Buscando almas silenciadas para liberar...**"
        )

        for miembro in ctx.guild.members:
            if miembro.timed_out_until is not None:
                try:
                    await miembro.edit(
                        timed_out_until=None,
                        reason=f"Liberado por AngelGuard de {ctx.author}",
                    )
                    count += 1
                except discord.DiscordException:
                    pass

        if count > 0:
            embed = discord.Embed(
                title="✨ AngelGuard Activo",
                description=(
                    f"Se ha restaurado el equilibrio.\n"
                    f"He devuelto la voz a **{count}** usuario(s)."
                ),
                color=discord.Color.gold(),
            )
            await status_msg.edit(content=None, embed=embed)
        else:
            await status_msg.edit(
                content="🙏 No hay nadie silenciado actualmente."
            )

    # ── Message Purge ────────────────────────────────────────────────────────
    @commands.command(name="mlshr")
    @commands.has_permissions(manage_messages=True)
    async def mlshr(self, ctx: commands.Context, amount: str) -> None:
        """Bulk-delete messages. Usage: cx!mlshr [N | all]"""
        try:
            if amount.lower() == "all":
                deleted = await ctx.channel.purge()
                count = len(deleted)
            else:
                num = int(amount)
                # +1 to also delete the command message
                deleted = await ctx.channel.purge(limit=num + 1)
                count = len(deleted) - 1  # exclude command message
        except (ValueError, discord.DiscordException) as e:
            await ctx.send(
                '❌ Indica un número o "all".',
                delete_after=5,
            )
            log.warning("Error en mlshr: %s", e)
            return

        await ctx.send(
            f"✅ Se han borrado {count} mensajes.",
            delete_after=5,
        )


async def setup(bot: commands.Bot) -> None:
    """Load the Moderacion cog."""
    await bot.add_cog(Moderacion(bot))
