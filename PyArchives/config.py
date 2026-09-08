"""Backwards-compatible config shim.

New code should import from ``core.settings``. This module
re-exports the same names so existing ``from config import X``
imports keep working unchanged.
"""
from core.settings import (  # noqa: F401
    ADMIN_ID,
    AURA_DATA_PATH,
    BACKUP_DIR,
    BASE_DIR,
    BLACKLIST_PATH,
    CANAL_ANUNCIOS_ID,
    CANAL_BOT_ID,
    COMMAND_PREFIX,
    CONFIG_WARNINGS,
    COOLDOWN_AI,
    COOLDOWN_ALABA,
    COOLDOWN_AURA,
    COOLDOWN_CASTIGO,
    COOLDOWN_HOLA,
    COOLDOWN_PICHA,
    COOLDOWN_RULETA,
    COOLDOWN_VS,
    DISCORD_TOKEN,
    ENABLE_WEB,
    GROQ_API_KEY,
    GROQ_MAX_TOKENS,
    GROQ_MODEL,
    LOG_DIR,
    MAINTENANCE_PATH,
    MAX_INPUT_CHARS,
    MAX_PURGE_AMOUNT,
    MAX_REMINDER_SECONDS,
    MAX_SAY_CHARS,
    PORT,
    PURGE_CONFIRM_SECONDS,
    SHIP_DATA_PATH,
    VCBAN_PATH,
)
