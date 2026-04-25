import discord
from discord.ext import commands
from comandos_gifs import bf, de


class Jujutsu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bf", aliases=["blackflash"])
    async def bf_command(self, ctx, usuario: discord.Member = None):
        """Ejecuta un Black Flash"""
        await bf(ctx, usuario)

    @commands.command(name="de", aliases=["dominio"])
    async def de_command(self, ctx, usuario: discord.Member = None):
        """Ejecuta una Expansión de Dominio"""
        await de(ctx, usuario)


async def setup(bot):
    await bot.add_cog(Jujutsu(bot))
