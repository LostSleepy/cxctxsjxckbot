import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random

# Cargar variables del archivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')  # Carga el token desde .env

# Configura el prefijo del bot y crea una instancia de `commands.Bot`
intents = discord.Intents.default()
intents.message_content = True  # Habilita el acceso al contenido de los mensajes
bot = commands.Bot(command_prefix="!", intents=intents)

# Listas de GIFs para Black Flash y Domain Expansion
black_flash_gifs = [
    "https://media1.tenor.com/m/-nZnQBzGa7EAAAAd/jujutsu-kaisen-jujutsu-kaisen-season-2.gif",
    "https://media1.tenor.com/m/K4zh-8HS-GYAAAAC/satoru-gojo-gojo-satoru.gif",
    "https://media.giphy.com/media/black_flash_3.gif"
]

domain_expansion_gifs = [
    "https://media.giphy.com/media/domain_expansion_1.gif",
    "https://media.giphy.com/media/domain_expansion_2.gif",
    "https://media.giphy.com/media/domain_expansion_3.gif"
]

# Evento: Cuando el bot está listo
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

# Comando básico: !hola
@bot.command()
async def hola(ctx):
    await ctx.send(f'¡Hola, {ctx.author.mention}!')

# Comando básico: !adios
@bot.command()
async def adios(ctx):
    await ctx.send('¡Adiós! ¡Que tengas un buen día!')

# Comando básico: !hora
@bot.command()
async def hora(ctx):
    from datetime import datetime
    ahora = datetime.now()
    await ctx.send(f'Son las {ahora.strftime("%H:%M")}.')

# Comando básico: !repetir
@bot.command()
async def repetir(ctx, *, mensaje: str):
    await ctx.send(f'Has dicho: {mensaje}')

# Comando: !bf (Black Flash)
@bot.command()
async def bf(ctx):
    gif = random.choice(black_flash_gifs)
    await ctx.send(gif)

# Comando: !de (Domain Expansion)
@bot.command()
async def de(ctx):
    gif = random.choice(domain_expansion_gifs)
    await ctx.send(gif)

# Ejecuta el bot con el token cargado
bot.run(TOKEN)