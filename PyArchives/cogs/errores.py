"""
Global error handler cog for the Teto Discord bot.
Catches and responds to all command errors with user-friendly messages.
"""
import logging
from typing import Optional

import discord
from discord.ext import commands

from config import ADMIN_ID

log = logging.getLogger(__name__)


class Errores(commands.Cog):
    """Centralized error handling for all command errors."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError,
    ) -> None:
        """Global error handler — processes all command errors."""
        # If the command has its own handler, skip
        if hasattr(ctx.command, "on_error"):
            return

        # Unwrap the original exception if applicable
        original: Optional[BaseException] = getattr(error, "original", None)
        error = original or error

        # ── Silent ignores ───────────────────────────────────────────────────
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.CheckFailure):
            return

        # ── User-facing errors ───────────────────────────────────────────────
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"❌ Te falta el argumento **{error.param.name}**.\n"
                f"Uso: `cx!{ctx.command.name} {ctx.command.signature}`"
            )
            return

        if isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ No encuentro a ese usuario.")
            return

        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Argumento inválido. Comprueba la mención.")
            return

        if isinstance(error, commands.MissingPermissions):
            perms = ", ".join(error.missing_permissions)
            await ctx.send(f"❌ No tienes permisos: `{perms}`")
            return

        if isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join(error.missing_permissions)
            await ctx.send(f"❌ Al bot le faltan permisos: `{perms}`")
            return

        if isinstance(error, commands.NotOwner):
            await ctx.send("❌ Solo el dueño puede usar esto.")
            return

        if isinstance(error, commands.CommandOnCooldown):
            # The admin bypass is handled at the cog level
            if ctx.author.id == ADMIN_ID:
                return
            await ctx.send(
                f"⏳ Espera **{error.retry_after:.1f}s** antes de volver a usarlo."
            )
            return

        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Este comando no funciona en DMs.")
            return

        # ── Unexpected errors → log and notify ───────────────────────────────
        log.error(
            "Error en '%s' por %s (ID: %d): %s",
            ctx.command,
            ctx.author,
            ctx.author.id,
            error,
            exc_info=error,
        )
        await ctx.send("⚠️ Algo ha salido mal. El error ha sido registrado.")


async def setup(bot: commands.Bot) -> None:
    """Load the Errores cog."""
    await bot.add_cog(Errores(bot))
