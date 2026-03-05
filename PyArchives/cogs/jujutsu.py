import discord
from discord.ext import commands
import sys
import os

# Esto añade la carpeta superior al camino de búsqueda de Python de forma dinámica
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from comandos_gifs import bf, de


class Jujutsu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="de", aliases=["dominio"])
    async def de_command(self, ctx, usuario: discord.Member = None):
        """Ejecuta una Expansión de Dominio"""
        # Verificamos que la función 'de' exista antes de llamarla
        try:
            await de(ctx, usuario)
        except Exception as e:
            await ctx.send(f"❌ Error al ejecutar Dominio: {e}")

    @commands.command(name="bf", aliases=["blackflash"])
    async def bf_command(self, ctx, usuario: discord.Member = None):
        """Ejecuta un Black Flash"""
        try:
            await bf(ctx, usuario)
        except Exception as e:
            await ctx.send(f"❌ Error al ejecutar Black Flash: {e}")


async def setup(bot):
    await bot.add_cog(Jujutsu(bot))
