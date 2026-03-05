import discord
from discord.ext import commands
import random
from datetime import timedelta


class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ruleta"])
    async def ruleta_rusa(self, ctx):
        """Versión con diagnóstico para ver por qué no funciona."""

        # LOG de inicio
        print(f"DEBUG: Comando ejecutado por {ctx.author.name}")

        if not ctx.author.voice:
            return await ctx.send("❌ Error: No detecto que estés en un canal de voz.")

        canal = ctx.author.voice.channel
        # Forzamos la obtención de miembros si el caché está vacío
        miembros = canal.members

        print(
            f"DEBUG: Canal detectado: {canal.name}. Miembros encontrados: {len(miembros)}"
        )

        # Filtro simplificado para pruebas
        victimas = [m for m in miembros if not m.bot]

        if not victimas:
            return await ctx.send(
                f"❌ No encontré víctimas humanas en `{canal.name}`. ¿Tienes los Privileged Intents activos?"
            )

        elegido = random.choice(victimas)
        await ctx.send(f"🎲 La ruleta gira... apuntando a {elegido.mention}")

        try:
            await elegido.move_to(None)
            await ctx.send(
                f"💥 {elegido.display_name} ha sido expulsado de la llamada."
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ No tengo permisos (Mover Miembros) para desconectar a esa persona."
            )
        except Exception as e:
            await ctx.send(f"⚠️ Error inesperado: {e}")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def angelguard(self, ctx):
        """Quita el timeout a todos los usuarios silenciados del servidor."""
        count = 0
        status_msg = await ctx.send("😇 **Buscando almas silenciadas para liberar...**")

        for miembro in ctx.guild.members:
            if miembro.timed_out_until is not None:
                try:
                    await miembro.edit(
                        timed_out_until=None,
                        reason=f"Liberado por AngelGuard de {ctx.author}",
                    )
                    count += 1
                except:
                    pass

        if count > 0:
            embed = discord.Embed(
                title="✨ AngelGuard Activo",
                description=f"Se ha restaurado el equilibrio.\nHe devuelto la voz a **{count}** usuario(s).",
                color=discord.Color.gold(),
            )
            await status_msg.edit(content=None, embed=embed)
        else:
            await status_msg.edit(content="🙏 No hay nadie silenciado actualmente.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def mlshr(self, ctx, amount: str):
        """Borra mensajes del chat."""
        if amount.lower() == "all":
            await ctx.channel.purge()
            await ctx.send("✅ Chat purificado correctamente.", delete_after=5)
        else:
            try:
                num = int(amount)
                # Sumamos 1 para borrar también el mensaje del comando
                await ctx.channel.purge(limit=num + 1)
                await ctx.send(f"✅ Se han borrado {num} mensajes.", delete_after=5)
            except:
                await ctx.send('❌ Indica un número o "all".', delete_after=5)


async def setup(bot):
    await bot.add_cog(Moderacion(bot))
