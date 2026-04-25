import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import logging
from flask import Flask
from threading import Thread

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# --- SERVIDOR WEB ---
app = Flask(__name__)


@app.route("/")
def home():
    return "Bot está vivo!"


def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    t = Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True)
    t.start()


# ---------------------

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN no está definido en las variables de entorno.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="cx!", intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    log.info(f"Bot encendido como {bot.user} (ID: {bot.user.id})")


async def load_extensions():
    cogs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cogs")
    if not os.path.exists(cogs_path):
        log.error(f"No se encontró la carpeta 'cogs' en: {cogs_path}")
        return
    for filename in os.listdir(cogs_path):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                log.info(f"Extensión cargada: {filename}")
            except Exception as e:
                log.warning(f"Error cargando {filename}: {e}")


async def main():
    async with bot:
        keep_alive()
        await load_extensions()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
