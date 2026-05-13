"""
Teto — Sukuna's Vessel
A multi-functional Discord bot inspired by Jujutsu Kaisen and Kasane Teto.

Entry point: initializes the bot, loads extensions, and starts the web server.
"""
import asyncio
import logging
import os

import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

from config import COMMAND_PREFIX, DISCORD_TOKEN, PORT
from utils.logger import setup_logger

# ── Logging ────────────────────────────────────────────────────────────────────
log = setup_logger("teto")

# ── Web Server (for free hosting keep-alive) ──────────────────────────────────
app = Flask(__name__)


@app.route("/")
def home() -> str:
    """Health-check endpoint."""
    return "Bot está vivo!"


def keep_alive() -> None:
    """Start the Flask web server in a background daemon thread."""
    t = Thread(
        target=lambda: app.run(host="0.0.0.0", port=PORT),
        daemon=True,
    )
    t.start()
    log.info("Servidor web iniciado en puerto %d", PORT)


# ── Bot Setup ─────────────────────────────────────────────────────────────────
if not DISCORD_TOKEN:
    log.critical("DISCORD_TOKEN no está definido en las variables de entorno.")
    raise RuntimeError("DISCORD_TOKEN no está definido en las variables de entorno.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready() -> None:
    """Log when the bot comes online."""
    log.info(
        "Bot encendido como %s (ID: %s)",
        bot.user,
        bot.user.id,
    )


async def load_extensions() -> None:
    """Discover and load all cog modules from the 'cogs' directory."""
    cogs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cogs")
    if not os.path.exists(cogs_path):
        log.error("No se encontró la carpeta 'cogs' en: %s", cogs_path)
        return

    loaded = 0
    for filename in sorted(os.listdir(cogs_path)):
        if filename.endswith(".py") and not filename.startswith("__"):
            extension = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(extension)
                log.info("Extensión cargada: %s", filename)
                loaded += 1
            except Exception as e:
                log.warning("Error cargando %s: %s", filename, e)

    log.info("Cogs cargados: %d/%d", loaded, loaded)


async def main() -> None:
    """Initialize the bot, web server, and start the client."""
    async with bot:
        keep_alive()
        await load_extensions()
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
