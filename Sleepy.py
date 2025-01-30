import discord
from discord.ext import commands
from comandos_gifs import bf, de, rangif
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')  # Carga el token desde .env

# Configura el prefijo del bot y crea una instancia de `commands.Bot`
intents = discord.Intents.default()
intents.message_content = True  # Habilita el acceso al contenido de los mensajes
bot = commands.Bot(command_prefix="!", intents=intents)

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
    
# Ejecuta el bot con el token cargado
bot.run(TOKEN)