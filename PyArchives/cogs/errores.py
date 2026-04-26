import discord
from discord.ext import commands
import logging

log = logging.getLogger(__name__)
ADMIN_ID = 979869404110159912


class Errores(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(
                f"❌ Te falta el argumento **{error.param.name}**.\n"
                f"Uso: `cx!{ctx.command.name} {ctx.command.signature}`"
            )

        if isinstance(error, commands.MemberNotFound):
            return await ctx.send("❌ No encuentro a ese usuario.")

        if isinstance(error, commands.BadArgument):
            return await ctx.send("❌ Argumento inválido. Comprueba la mención.")

        if isinstance(error, commands.MissingPermissions):
            perms = ", ".join(error.missing_permissions)
            return await ctx.send(f"❌ No tienes permisos: `{perms}`")

        if isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join(error.missing_permissions)
            return await ctx.send(f"❌ Al bot le faltan permisos: `{perms}`")

        if isinstance(error, commands.NotOwner):
            return await ctx.send("❌ Solo el dueño puede usar esto.")

        if isinstance(error, commands.CommandOnCooldown):
            # El admin nunca ve este mensaje — el bypass se hace en cada cog
            if ctx.author.id == ADMIN_ID:
                return
            return await ctx.send(
                f"⏳ Espera **{error.retry_after:.1f}s** antes de volver a usarlo."
            )

        if isinstance(error, commands.NoPrivateMessage):
            return await ctx.send("❌ Este comando no funciona en DMs.")

        if isinstance(error, commands.CheckFailure):
            return

        log.error(f"Error en '{ctx.command}' por {ctx.author}: {error}", exc_info=error)
        await ctx.send("⚠️ Algo ha salido mal. El error ha sido registrado.")


async def setup(bot):
    await bot.add_cog(Errores(bot))
