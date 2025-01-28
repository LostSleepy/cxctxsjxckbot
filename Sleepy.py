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

# Evento: Cuando el bot está listo
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

# Comando bf!
@bot.command(name="bf")
async def black_flash(ctx, user: discord.Member):
    # Lista de GIFs predefinidos
    gifs = [
        "https://media1.tenor.com/m/-nZnQBzGa7EAAAAd/jujutsu-kaisen-jujutsu-kaisen-season-2.gif",
        "https://media1.tenor.com/m/IfLc43H57IMAAAAd/jjk-jjk-s2.gif",
        "https://media1.tenor.com/m/SA78kvgb6SIAAAAd/nanami-nanami-kento.gif", 
        "https://media1.tenor.com/m/K4zh-8HS-GYAAAAd/satoru-gojo-gojo-satoru.gif",
        "https://media1.tenor.com/m/wgHrYBAAuzUAAAAd/jjk0-yuta.gif"
    ]
    
    # Seleccionar un GIF aleatoriamente
    gif_seleccionado = random.choice(gifs)

    # Crear un embed
    embed = discord.Embed(
        title="¡Black Flash!",
        description=f"{ctx.author.mention} usó **Black Flash** contra {user.mention} ⚡",
        color=discord.Color.red()
    )
    embed.set_image(url=gif_seleccionado)

    # Enviar el embed
    await ctx.send(embed=embed)
    
# Comando de
@bot.command(name="de")
async def black_flash(ctx, user: discord.Member):
    # Lista de GIFs predefinidos
    gifs = [
        "https://media1.tenor.com/m/MuMLDWrW95gAAAAd/gojo-domain-expansion.gif",
        "https://media1.tenor.com/m/RAp5YpmEH5EAAAAd/jujutsu-kaisen-shibuya-arc-sukuna-shibuya-arc.gif",
        "https://media1.tenor.com/m/G_HN1fYl61kAAAAd/domain-expansion-yuta.gif", 
        "https://media1.tenor.com/m/09i4-rohmdAAAAAd/kenjaku-geto-suguru.gif",
        "https://media1.tenor.com/m/3fzEJTA3ykUAAAAd/hakari-kinji-kinji-hakari.gif",
        "https://media1.tenor.com/m/EJW3gcpVvWgAAAAd/jogo-domain-expansion.gif",
        "https://media1.tenor.com/m/rzLycKqpA_EAAAAd/mahito-domain-expansion.gif",
    ]
    
    # Seleccionar un GIF aleatoriamente
    gif_seleccionado = random.choice(gifs)

    # Crear un embed
    embed = discord.Embed(
        title="¡EXPANSION DE DOMINIO!",
        description=f"{ctx.author.mention} usó su **Expansion de dominio** contra {user.mention} 😯😯",
        color=discord.Color.blue()
    )
    embed.set_image(url=gif_seleccionado)

    # Enviar el embed
    await ctx.send(embed=embed)
    

# Ejecuta el bot con el token cargado
bot.run(TOKEN)
