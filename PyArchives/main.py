"""
Teto — bot multifuncional de Discord.

Entry point: initializes the bot, wires persistent state,
loads extensions, optionally starts the keep-alive web server.
"""

import asyncio
import time
from threading import Thread

import discord
from config import (
    BLACKLIST_PATH,
    COMMAND_PREFIX,
    CONFIG_WARNINGS,
    DISCORD_TOKEN,
    ENABLE_WEB,
    MAINTENANCE_PATH,
    PORT,
)
from core.http import close_session
from discord.ext import commands
from flask import Flask
from services.state import Blacklist, Maintenance
from utils.logger import setup_logger

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
        target=lambda: app.run(host="0.0.0.0", port=PORT, use_reloader=False),
        daemon=True,
    )
    t.start()
    log.info("Servidor web iniciado en puerto %d", PORT)


# ── Bot ───────────────────────────────────────────────────────────────────────
class TetoBot(commands.Bot):
    """Bot with shared persistent state and a global access check."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)
        self.remove_command("help")
        self.start_time: float = time.time()
        self.blacklist = Blacklist(BLACKLIST_PATH)
        self.maintenance = Maintenance(MAINTENANCE_PATH)

    async def on_ready(self) -> None:
        user = self.user
        log.info("Bot encendido como %s (ID: %s)", user, user.id if user else "?")
        for warning in CONFIG_WARNINGS:
            log.warning("Config: %s", warning)

    async def close(self) -> None:
        try:
            await close_session()
        finally:
            await super().close()


bot = TetoBot()


@bot.check_once
async def _global_access_check(ctx: commands.Context) -> bool:
    """Block blacklisted users and (in maintenance) everyone but the admin."""
    from config import ADMIN_ID

    try:
        if ctx.author.id == ADMIN_ID or await bot.is_owner(ctx.author):
            return True
    except Exception:
        from config import ADMIN_ID as _ADMIN

        if ctx.author.id == _ADMIN:
            return True
    if await bot.blacklist.is_blocked(ctx.author.id):
        try:
            await ctx.send("🚫 Estás bloqueado y no puedes usar comandos del bot.", delete_after=5)
        except discord.DiscordException:
            pass
        return False
    if await bot.maintenance.is_enabled():
        try:
            await ctx.send("⚙️ Teto está en **mantenimiento**. Prueba más tarde.", delete_after=8)
        except discord.DiscordException:
            pass
        return False
    return True


COGS: tuple[str, ...] = (
    "cogs.aura",
    "cogs.extras",
    "cogs.utilidad",
    "cogs.moderacion",
    "cogs.admin",
    "cogs.apis",
    "cogs.fortnite",
    "cogs.ia",
    "cogs.errores",
)


async def load_extensions() -> None:
    """Load all known cog modules, logging failures loudly."""
    loaded, failed = 0, 0
    for extension in COGS:
        try:
            await bot.load_extension(extension)
            log.info("Extensión cargada: %s", extension)
            loaded += 1
        except Exception as e:
            failed += 1
            log.error("Error cargando %s: %s", extension, e, exc_info=True)
    log.info("Cogs cargados: %d ok, %d fallidos", loaded, failed)


async def main() -> None:
    """Initialize the bot, web server, and start the client."""
    if not DISCORD_TOKEN:
        log.critical("DISCORD_TOKEN no está definido en las variables de entorno.")
        raise RuntimeError("DISCORD_TOKEN no está definido en las variables de entorno.")
    async with bot:
        if ENABLE_WEB:
            keep_alive()
        await load_extensions()
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
