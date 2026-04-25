import discord
from discord.ext import commands
import logging

log = logging.getLogger(__name__)


class Errores(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Si el comando tiene su propio error handler, no hacemos nada
        if hasattr(ctx.command, "on_error"):
            return

        # Desenvolvemos el error si viene envuelto
        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return  # Silencioso

        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(
                f"❌ Te falta el argumento **{error.param.name}**.\n"
                f"Uso correcto: `cx!{ctx.command.name} {ctx.command.signature}`"
            )

        if isinstance(error, commands.MemberNotFound):
            return await ctx.send("❌ No encuentro a ese usuario. Menciona a alguien del servidor.")

        if isinstance(error, commands.BadArgument):
            return await ctx.send("❌ Argumento inválido. Comprueba que estás mencionando bien al usuario.")

        if isinstance(error, commands.MissingPermissions):
            perms = ", ".join(error.missing_permissions)
            return await ctx.send(f"❌ No tienes permisos para esto: `{perms}`")

        if isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join(error.missing_permissions)
            return await ctx.send(f"❌ Al bot le faltan permisos: `{perms}`")

        if isinstance(error, commands.NotOwner):
            return await ctx.send("❌ Solo el dueño del bot puede usar esto.")

        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(
                f"⏳ Tranquilo, espera **{error.retry_after:.1f}s** antes de volver a usarlo."
            )

        if isinstance(error, commands.NoPrivateMessage):
            return await ctx.send("❌ Este comando no funciona en mensajes privados.")

        if isinstance(error, commands.CheckFailure):
            return  # Silencioso (ej: el check de ID en cita)

        # Error inesperado — lo loggeamos
        log.error(f"Error en '{ctx.command}' por {ctx.author}: {error}", exc_info=error)
        await ctx.send("⚠️ Algo ha salido mal. El error ha sido registrado.")


async def setup(bot):
    await bot.add_cog(Errores(bot))
