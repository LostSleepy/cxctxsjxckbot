import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

# Carga las variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# CONFIGURACIÓN DE INTENTS
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  
# CAMBIO DE PREFIJO AQUÍ:
bot = commands.Bot(command_prefix="cx!", intents=intents)
bot.remove_command('help') # Esto quita el comando !help por defecto

@bot.event
async def on_ready():
    print(f'✅ Bot encendido como {bot.user.name}')
    print(f'Prefijo configurado: cx!')

async def load_extensions():
    """Busca los Cogs usando una ruta absoluta para evitar errores"""
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
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())