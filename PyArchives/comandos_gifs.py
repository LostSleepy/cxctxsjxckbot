# Comando: !bf (Black Flash)
import discord
import os
import random

TENOR_API_KEY = os.getenv('TENOR_API_KEY')

# Listas de GIFs para Black Flash y Domain Expansion
black_flash_gifs = [
    "https://media1.tenor.com/m/-nZnQBzGa7EAAAAd/jujutsu-kaisen-jujutsu-kaisen-season-2.gif",
    "https://media1.tenor.com/m/K4zh-8HS-GYAAAAC/satoru-gojo-gojo-satoru.gif",
    "https://media1.tenor.com/m/OEW-T6-aHGQAAAAd/yuta-black-flash-yuta.gif",
    "https://media1.tenor.com/m/SA78kvgb6SIAAAAC/nanami-nanami-kento.gif",
    "https://media1.tenor.com/m/IfLc43H57IMAAAAd/jjk-jjk-s2.gif",
    "https://media1.tenor.com/m/0EERvw7z2aEAAAAC/jjk-jjk-s2.gif",
]

domain_expansion_gifs = [
    "https://media1.tenor.com/m/MuMLDWrW95gAAAAd/gojo-domain-expansion.gif",
    "https://media1.tenor.com/m/EJW3gcpVvWgAAAAd/jogo-domain-expansion.gif",
    "https://media1.tenor.com/m/rzLycKqpA_EAAAAd/mahito-domain-expansion.gif",
    "https://media1.tenor.com/m/G_HN1fYl61kAAAAd/domain-expansion-yuta.gif",
    "https://media1.tenor.com/m/09i4-rohmdAAAAAd/kenjaku-geto-suguru.gif",
    "https://media1.tenor.com/m/VVYqjYeE0LYAAAAd/yuji-domain-yuji-vs-sukuna.gif",
    "https://media1.tenor.com/m/RAp5YpmEH5EAAAAd/jujutsu-kaisen-shibuya-arc-sukuna-shibuya-arc.gif",
    "https://media1.tenor.com/m/cntrkc6Ti0AAAAAd/gojo-domain-expansion.gif"
]
# Funciones de comandos
async def bf(ctx, usuario: discord.Member = None):  # No necesita el decorador aquí
    if usuario is None:
        await ctx.send("Debes mencionar a un usuario para usar este comando.")
        return

    gif = random.choice(black_flash_gifs)
    embed = discord.Embed(
        title="⚡¡Black Flash!⚡",
        description=f"{ctx.author.mention} le ha hecho un **Black Flash** a {usuario.mention}.⚡",
        color=discord.Color.red()
    )
    embed.set_image(url=gif)
    await ctx.send(embed=embed)

async def de(ctx, usuario: discord.Member = None):  # No necesita el decorador aquí
    if usuario is None:
        await ctx.send("Debes mencionar a un usuario para usar este comando.")
        return

    gif = random.choice(domain_expansion_gifs)
    embed = discord.Embed(
        title="¡EXPANSION DE DOMINIO!",
        description=f"{ctx.author.mention} le ha expandido su **dominio** a {usuario.mention}",
        color=discord.Color.blue()
    )
    embed.set_image(url=gif)
    await ctx.send(embed=embed)