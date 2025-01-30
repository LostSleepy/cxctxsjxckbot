# Comando: !bf (Black Flash)
import discord
import os
import random
import requests
from discord.ext import commands
TENOR_API_KEY = os.getenv('TENOR_API_KEY')  # API Key de Tenor
# Configura el prefijo del bot y crea una instancia de `commands.Bot`
intents = discord.Intents.default()
intents.message_content = True  # Habilita el acceso al contenido de los mensajes
bot = commands.Bot(command_prefix="!", intents=intents)

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

@bot.command()
async def bf(ctx, usuario: discord.Member = None):
    if usuario is None:
        await ctx.send("Debes mencionar a un usuario para usar este comando.")
        return

    # Selecciona un GIF aleatorio
    gif = random.choice(black_flash_gifs)

    # Crea un embed
    embed = discord.Embed(
        title="⚡¡Black Flash!⚡",
        description=f"{ctx.author.mention} le ha hecho un **Black Flash** a {usuario.mention}.⚡",
        color=discord.Color.red()  # Color del embed (rojo en este caso)
    )
    embed.set_image(url=gif)  # Añade el GIF al embed

    # Envía el embed
    await ctx.send(embed=embed)

# Comando: !de (Domain Expansion)
@bot.command()
async def de(ctx, usuario: discord.Member = None):
    if usuario is None:
        await ctx.send("Debes mencionar a un usuario para usar este comando.")
        return

    gif = random.choice(domain_expansion_gifs)
    # Crea un embed
    embed = discord.Embed(
        title="¡EXPANSION DE DOMINIO!",
        description=f"{ctx.author.mention} le ha expandido su **dominio** a {usuario.mention}",
        color=discord.Color.blue()  # Color del embed (rojo en este caso)
    )
    embed.set_image(url=gif)  # Añade el GIF al embed

    # Envía el embed
    await ctx.send(embed=embed)

@bot.command()
async def rangif(ctx, *, search_term: str):
    # Límite de resultados (puedes ajustarlo)
    limit = 20

    # Hacer la solicitud a la API de Tenor
    url = f"https://tenor.googleapis.com/v2/search?q={search_term}&key={TENOR_API_KEY}&limit={limit}"
    response = requests.get(url)

    if response.status_code == 200:  # Si la solicitud es exitosa
        data = response.json()
        gifs = data.get("results", [])

        if gifs:
            # Seleccionar un GIF aleatorio
            gif = random.choice(gifs)
            gif_url = gif["media_formats"]["gif"]["url"]

            # Enviar el GIF
            await ctx.send(gif_url)
        else:
            await ctx.send(f"No se encontraron GIFs para '{search_term}'.")
    else:
        await ctx.send("Hubo un error al buscar GIFs en Tenor. Inténtalo de nuevo más tarde.")