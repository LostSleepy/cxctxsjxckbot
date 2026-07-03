"""
Centralized configuration for the Teto Discord bot.
All constants, IDs, file paths, and environment variables are defined here.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Bot ---
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
COMMAND_PREFIX: str = "cx!"

# --- Admin ---
ADMIN_ID: int = int(os.getenv("ADMIN_ID", "979869404110159912"))

# --- Channel IDs ---
CANAL_ANUNCIOS_ID: int = 1497645495051354113

# --- File Paths ---
BASE_DIR: Path = Path(__file__).resolve().parent
AURA_DATA_PATH: Path = BASE_DIR / "aura_data.json"
SHIP_DATA_PATH: Path = BASE_DIR / "ship_data.json"
BLACKLIST_PATH: Path = BASE_DIR / "blacklist.json"
MAINTENANCE_PATH: Path = BASE_DIR / "maintenance.json"

# --- APIs ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = "llama-3.3-70b-versatile"
GROQ_MAX_TOKENS: int = 200

# --- Web Server ---
PORT: int = int(os.getenv("PORT", "8080"))

# --- Limits ---
MAX_REMINDER_SECONDS: int = 86400       # 24 horas
