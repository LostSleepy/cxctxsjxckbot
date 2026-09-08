"""Centralized, validated configuration.

Single source of truth. The legacy ``config.py`` re-exports these
symbols so existing ``from config import X`` imports keep working.

All values come from the environment (``.env`` supported) with
safe defaults. Invalid values never crash the import: they fall
back to defaults and are reported via ``CONFIG_WARNINGS``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent.parent

CONFIG_WARNINGS: list[str] = []


def _warn(msg: str) -> None:
    CONFIG_WARNINGS.append(msg)


def _get_int(
    name: str, default: int, minimum: int | None = None, maximum: int | None = None
) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        _warn(f"{name}={raw!r} no es un entero; usando {default}.")
        return default
    if minimum is not None and value < minimum:
        _warn(f"{name}={value} menor que {minimum}; usando {minimum}.")
        return minimum
    if maximum is not None and value > maximum:
        _warn(f"{name}={value} mayor que {maximum}; usando {maximum}.")
        return maximum
    return value


def _get_str(name: str, default: str) -> str:
    return os.getenv(name, default) or default


def _get_snowflake(name: str, default: int) -> int:
    """Parse a Discord snowflake ID; 0 means 'not configured'."""
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        _warn(f"{name}={raw!r} no es un ID válido; usando valor por defecto.")
        return default
    if value < 0:
        _warn(f"{name}={value} inválido; usando valor por defecto.")
        return default
    return value


# --- Bot ---
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
COMMAND_PREFIX: str = _get_str("COMMAND_PREFIX", "cx!")

# --- Admin ---
ADMIN_ID: int = _get_int("ADMIN_ID", 979869404110159912, minimum=1)

# --- Channels (0 = not configured) ---
CANAL_ANUNCIOS_ID: int = _get_snowflake("CANAL_ANUNCIOS_ID", 1497645495051354113)
CANAL_BOT_ID: int = _get_snowflake("CANAL_BOT_ID", 1432506760698003466)

# --- Paths ---
AURA_DATA_PATH: Path = BASE_DIR / "aura_data.json"
SHIP_DATA_PATH: Path = BASE_DIR / "ship_data.json"
BLACKLIST_PATH: Path = BASE_DIR / "blacklist.json"
MAINTENANCE_PATH: Path = BASE_DIR / "maintenance.json"
VCBAN_PATH: Path = BASE_DIR / "vcban.json"
LOG_DIR: Path = BASE_DIR / "logs"
BACKUP_DIR: Path = BASE_DIR / "backups"

# --- AI ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = _get_str("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_MAX_TOKENS: int = _get_int("GROQ_MAX_TOKENS", 200, minimum=16, maximum=1024)

# --- Web keep-alive ---
ENABLE_WEB: bool = os.getenv("ENABLE_WEB", "1") not in ("0", "false", "False", "no")
PORT: int = _get_int("PORT", 8080, minimum=1, maximum=65535)

# --- Limits ---
MAX_REMINDER_SECONDS: int = 86400  # 24h
MAX_INPUT_CHARS: int = 500  # generic user-text cap for API-bound commands
MAX_SAY_CHARS: int = 1900  # Discord message cap with margin
MAX_PURGE_AMOUNT: int = 100  # safety cap for cx!purge N
PURGE_CONFIRM_SECONDS: int = 30

# --- Cooldowns (seconds) ---
COOLDOWN_AURA: int = 30
COOLDOWN_PICHA: int = 30
COOLDOWN_HOLA: int = 10
COOLDOWN_ALABA: int = 10
COOLDOWN_VS: int = 20
COOLDOWN_CASTIGO: int = 3600
COOLDOWN_RULETA: int = 3600
COOLDOWN_AI: int = 3


@dataclass(frozen=True)
class Settings:
    """Immutable snapshot (useful for tests and diagnostics)."""

    command_prefix: str = COMMAND_PREFIX
    admin_id: int = ADMIN_ID
    groq_model: str = GROQ_MODEL
    port: int = PORT
    warnings: tuple[str, ...] = field(default_factory=lambda: tuple(CONFIG_WARNINGS))


def settings_snapshot() -> Settings:
    return Settings()
