"""
Moderation commands cog for the Teto Discord bot.
Includes voice roulette, AngelGuard timeout remover, message purge,
and the voice softban toggle system.
"""
import json
import logging
import random
from typing import List, Set

import discord
from discord.ext import commands

from config import ADMIN_ID, VCBAN_PATH

log = logging.getLogger(__name__)


class Moderacion(commands.Cog):
    """Server moderation commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._vcban: Set[str] = self._load_vcban()

    # ── Voice ban persistence ─────────────────────────────────────────────────
    def _load_vcban(self) -> Set[str]:
        """Load voice-banned user IDs from JSON."""
        if not VCBAN_PATH.exists():
            return set()
        try:
            with open(VCBAN_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return set(data.get("banned", []))
        except (json.JSONDecodeError, OSError):
            return set()

    def _save_vcban(self) -> None:
        """Save voice-banned user IDs to JSON atomically."""
        temp = VCBAN_PATH.with_suffix(".tmp")
        with open(temp, "w", encoding="utf-8") as f:
            json.dump({"banned": list(self._vcban)}, f, indent=2)
        temp.replace(VCBAN_PATH)

    # ── Admin Cooldown Bypass ────────────────────────────────────────────────
    async def _bypass_cooldown(self, ctx: commands.Context) -> None:
        """Remove cooldown for the configured admin."""
        if ctx.author.id == ADMIN_ID:
            ctx.command.reset_cooldown(ctx)

    # ── Russian Roulette (voice kick) ────────────────────────────────────────
    @commands.command(name="ruleta", aliases=["ruleta_rusa"])
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def ruleta_rusa(self, ctx: commands.Context) -> None:
        """Randomly kick a member from your voice channel."""
        await self._bypass_cooldown(ctx)
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

    # ── Voice SoftBan (admin only) ─────────────────────────────────────────
    @commands.command(name="vckick", aliases=["vcsoftban"])
    async def vc_kick(self, ctx: commands.Context, usuario: discord.Member = None) -> None:
        """[Admin] Toggle voice ban para un usuario.
        Si está en la lista, lo elimina. Si no, lo añade.
        Los usuarios en la lista son expulsados automáticamente
        cada vez que intenten unirse a un canal de voz.

        Uso: `cx!vckick`         — muestra la lista
             `cx!vckick @usuario` — añade/remueve
        """
        if ctx.author.id != ADMIN_ID:
            return

        # ── Show list (no args) ──────────────────────────────────────────
        if usuario is None:
            if not self._vcban:
                await ctx.send("📋 No hay usuarios baneados de voz.")
                return

            lines = []
            guild = ctx.guild
            for uid in sorted(self._vcban):
                member = guild.get_member(int(uid)) if guild else None
                name = member.display_name if member else f"ID: {uid}"
                lines.append(f"• {name} (`{uid}`)")

            embed = discord.Embed(
                title=f"👢 Voice Ban List ({len(self._vcban)})",
                description="\n".join(lines),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        # ── Validate member ──────────────────────────────────────────────
        if usuario.bot:
            await ctx.send("❌ No puedes banear bots de voz.")
            return

        uid = str(usuario.id)

        # ── Toggle ───────────────────────────────────────────────────────
        if uid in self._vcban:
            self._vcban.discard(uid)
            self._save_vcban()
            # Also kick them right now if they're in voice
            if usuario.voice:
                try:
                    canal = usuario.voice.channel
                    await usuario.move_to(None)
                    await ctx.send(
                        f"✅ {usuario.mention} removido de la voice ban list "
                        f"y expulsado de **{canal.name}**."
                    )
                except discord.DiscordException:
                    pass
            else:
                await ctx.send(
                    f"✅ {usuario.mention} removido de la voice ban list."
                )
        else:
            self._vcban.add(uid)
            self._save_vcban()
            # Kick them immediately if they're in voice
            if usuario.voice:
                try:
                    canal = usuario.voice.channel
                    await usuario.move_to(None)
                    await ctx.send(
                        f"👢 {usuario.mention} añadido a la voice ban list "
                        f"y expulsado de **{canal.name}**."
                    )
                except discord.Forbidden:
                    await ctx.send(
                        f"👢 {usuario.mention} añadido a la voice ban list. "
                        "Pero no tengo permisos para expulsarlo ahora."
                    )
                except discord.DiscordException:
                    await ctx.send(
                        f"👢 {usuario.mention} añadido a la voice ban list."
                    )
            else:
                await ctx.send(
                    f"👢 {usuario.mention} añadido a la voice ban list. "
                    "Será expulsado automáticamente si se conecta a un canal."
                )

    # ── Voice listener: auto-kick banned users ────────────────────────────────
    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        """Automatically kick voice-banned users when they join a channel."""
        # Only act if they JOINED a voice channel (after.channel is not None)
        if after.channel is None:
            return

        uid = str(member.id)
        if uid not in self._vcban:
            return

        # Don't kick the admin by accident
        if member.id == ADMIN_ID:
            return

        log.info(
            "Auto-kick: %s (ID: %s) intentó unirse a %s — está en la voice ban list",
            member.display_name,
            member.id,
            after.channel.name,
        )

        try:
            await member.move_to(None)
            # Try to DM the user so they know why
            try:
                await member.send(
                    "👢 Has sido expulsado automáticamente del canal de voz "
                    "porque estás en la voice ban list del servidor."
                )
            except discord.Forbidden:
                pass
        except discord.Forbidden:
            log.warning(
                "No tengo permisos para expulsar a %s (baneado de voz)",
                member.display_name,
            )
        except discord.DiscordException as e:
            log.error("Error auto-kicking %s: %s", member.display_name, e)

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
    @commands.command(name="purge")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: str) -> None:
        """Bulk-delete messages. Usage: cx!purge [N | all]"""
        try:
            if amount.lower() == "all":
                deleted = await ctx.channel.purge()
                count = len(deleted)
            else:
                num = int(amount)
                # +1 to also delete the command message
                deleted = await ctx.channel.purge(limit=num + 1)
                # exclude command message; clamp to 0 in case nothing was deleted
                count = max(0, len(deleted) - 1)
        except (ValueError, discord.DiscordException) as e:
            await ctx.send(
                '❌ Indica un número o "all".',
                delete_after=5,
            )
            log.warning("Error en purge: %s", e)
            return

        await ctx.send(
            f"✅ Se han borrado {count} mensajes.",
            delete_after=5,
        )


async def setup(bot: commands.Bot) -> None:
    """Load the Moderacion cog."""
    await bot.add_cog(Moderacion(bot))
