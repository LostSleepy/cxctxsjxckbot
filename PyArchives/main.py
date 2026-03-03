import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from flask import Flask
from threading import Thread

# --- SERVIDOR WEB PARA EVITAR SUSPENSIÓN ---
app = Flask('')

@app.route('/')
def home():
    return "Bot está vivo!"

def run_web():
    # Usamos el puerto que Koyeb nos asigne o el 8080 por defecto
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()
# ------------------------------------------

# Carga las variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# CONFIGURACIÓN DE INTENTS
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix="cx!", intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'✅ Bot encendido como {bot.user.name}')
    print(f'Prefijo configurado: cx!')

async def load_extensions():
    base_path = os.path.dirname(os.path.abspath(__file__))
    cogs_path = os.path.join(base_path, 'cogs')

    if not os.path.exists(cogs_path):
        print(f"❌ ERROR: No se encontró la carpeta 'cogs' en: {cogs_path}")
        return

    for filename in os.listdir(cogs_path):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'📦 Extensión cargada: {filename}')
            except Exception as e:
                print(f'⚠️ Error cargando {filename}: {e}')

async def main():
    async with bot:
        # Iniciamos el servidor web justo antes que el bot
        keep_alive() 
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())