import discord
from discord.ext import commands
from comandos_gifs import bf, de # Importamos tus funciones de GIFs

class Jujutsu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['de'])
    async def de_command(self, ctx, usuario: discord.Member = None):
        """Ejecuta una Expansión de Dominio"""
        await de(ctx, usuario)

    @commands.command(aliases=['bf'])
    async def bf_command(self, ctx, usuario: discord.Member = None):
        """Ejecuta un Black Flash"""
        await bf(ctx, usuario)

async def setup(bot):
    await bot.add_cog(Jujutsu(bot))