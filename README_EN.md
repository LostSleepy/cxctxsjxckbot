<div align="center">

# 🥖 Teto — Discord Bot

> *"Baked with love. Deployed with intent."*

**A multi-functional Discord bot inspired by Kasane Teto.**
Moderation, entertainment, AI chat, aura system, and a daily dose of chaos.

[![Prefix](https://img.shields.io/badge/Prefix-cx!-ff69b4?style=for-the-badge&logo=discord&logoColor=white)](.)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](.)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=for-the-badge&logo=discord&logoColor=white)](.)

---

🇪🇸 [Versión en Español](README.md)

</div>

---

## 🚀 Installation

Requirements: **Python 3.11+**.

```bash
git clone <your-repo>
cd cxctxsjxckbot

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # then fill in your keys
```

## ▶️ Running

```bash
python PyArchives/main.py
```

The bot loads all 9 cogs, starts the keep-alive web server (if `ENABLE_WEB=1`)
and connects to Discord. Without `DISCORD_TOKEN` it refuses to start with a clear message.

## ⚙️ Configuration

Everything lives in environment variables (see `.env.example`).
`PyArchives/core/settings.py` validates them: an invalid value **never crashes the bot** —
it falls back to the default and logs a warning.

| Variable | Default | Description |
|---|---|---|
| `DISCORD_TOKEN` | — | Discord bot token (required) |
| `GROQ_API_KEY` | — | Groq API key for AI chat (required for `cx!chat`) |
| `COMMAND_PREFIX` | `cx!` | Command prefix |
| `ADMIN_ID` | `979869404110159912` | Creator ID: bypasses cooldowns, blacklist and maintenance |
| `CANAL_ANUNCIOS_ID` | `1497645495051354113` | Announcements channel (`0` = disabled) |
| `CANAL_BOT_ID` | `1432506760698003466` | Internal channel (informational) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model |
| `GROQ_MAX_TOKENS` | `200` | Max tokens per reply (16–1024) |
| `ENABLE_WEB` | `1` | Keep-alive server for free hosting (`0` = off) |
| `PORT` | `8080` | Web server port |

---

## 🎮 Fun

| Command | Aliases | Description |
|---|---|---|
| `cx!aura [@user]` | — | Check your daily aura score (resets every 24h) |
| `cx!top` | `ranking`, `leaderboard` | Server aura ranking (top 10) |
| `cx!chat <message>` | `conversar` | Chat with Teto (Groq AI, max 500 chars) |
| `cx!de @user` | `dominio` | Domain Expansion on a target |
| `cx!bf @user` | `blackflash` | Black Flash (5% chance to double your aura + announcement) |
| `cx!castigo @user` | `cast` | Random punishment (mute / deaf / kick / timeout) — 1h cooldown |
| `cx!alaba [@user]` | `glaze`, `alabanza`, `cumplido` | Teto praises someone |
| `cx!picha [@user]` | `pp` | Scientific measurement — results vary daily |
| `cx!ship @u1 [@u2]` | — | Love compatibility between two users (persistent) |
| `cx!vs @u1 @u2` | `versus` | Decide who would win in a fight |
| `cx!8ball <question>` | `pregunta`, `ball` | Consult the mystical 8ball |
| `cx!elegir <options>` | — | Teto chooses between comma-separated options |
| `cx!hola` | `hello`, `hi` | Personalized greeting with GIF |

---

## ✨ Aura System

Your daily aura score resets every 24 hours with a new random value (-1000 to 5000).

- **`cx!aura`** — Check your daily aura.
- **`cx!top`** — Server top 10 ranking.
- **`cx!bf @user`** — A Black Flash has a 5% chance to double your aura.

---

## 🤖 AI Chat

Teto uses **Groq AI (Llama 3.3 70B Versatile)** to chat in Spanish.

| Command | Aliases | Description |
|---|---|---|
| `cx!chat <message>` | `conversar` | Chat with Teto in her unique personality |

*3s cooldown between AI messages. Without `GROQ_API_KEY` the command reports that AI is unavailable.*

---

## 🛠️ Utility

| Command | Aliases | Description |
|---|---|---|
| `cx!help` | — | Show the command panel |
| `cx!ping` | — | Bot latency and API response time |
| `cx!uptime` | — | How long Teto has been awake |
| `cx!avatar [@user]` | `av` | High-resolution profile picture |
| `cx!userinfo [@user]` | `user`, `info`, `u` | Detailed user info (admin can add `raw` for extra info) |
| `cx!hora` | — | World clock — Madrid, New York and Japan |
| `cx!servidor` | `server`, `serverinfo`, `guild`, `guildinfo` | Full server info |
| `cx!rol [@role]` | `role`, `roleinfo`, `rolinfo` | Detailed role info |
| `cx!recordar <time> <text>` | `rem`, `reminder` | Reminder: `30s`, `10m`, `2h`, `1d` (max 24h). E.g. `cx!recordar 10m feed the dog` |

---

## 🌐 APIs & Search

| Command | Aliases | API | Description |
|---|---|---|---|
| `cx!pokemon <name>` | `poke`, `pokedex` | PokeAPI | Pokémon info with Spanish types, stats and sprite 🔍 |
| `cx!pais <name>` | `country`, `país`, `paises` | REST Countries | Country info (capital, population, currency, timezones) 🌍 |
| `cx!clima <city>` | `weather`, `tiempo` | Open-Meteo | Current weather for a city 🌤️ |
| `cx!anime <name>` | `mal`, `myanimelist` | Jikan (MAL) | Search anime on MyAnimeList 🎬 |
| `cx!perro [breed]` | `dog`, `perrito`, `doggo` | Dog CEO | Random dog picture 🐕 |
| `cx!razas` | `breeds` | Dog CEO | List all available dog breeds 🐕 |
| `cx!coctel <name>` | `cocktail`, `coctail`, `drink` | TheCocktailDB | Cocktail recipe with ingredients 🍸 |
| `cx!coctelaleatorio` | `randomdrink`, `randomcoctel` | TheCocktailDB | Random cocktail 🍸 |
| `cx!espacio` | `space`, `nasa`, `apod` | NASA APOD | Astronomy picture of the day 🚀 |
| `cx!chiste` | `joke`, `chistes` | JokeAPI (es) | Random joke in Spanish 😂 |
| `cx!traducir <text>` | `translate`, `trad` | MyMemory | Translate text. Use `cx!traducir en\|hola` to pin a language 🌐 |
| `cx!receta <name>` | `recipe`, `comida` | TheMealDB | Food recipe with ingredients 🍳 |
| `cx!catfact` | `gatofact`, `factcat` | Cat Facts | Random cat fact 🐱 |
| `cx!definir <word>` | `define`, `dict` | FreeDictionaryAPI | Word definition (ES → EN fallback) 📖 |
| `cx!fn <name>` | `fortnite` | Fortnite-API + Fortnite.GG | Fortnite.GG-style cosmetic card: image, price, source, wishlists, rating 🎮 |
| `cx!fn video <name>` | `fn v` | Fortnite-API + Fortnite.GG | Dance video: inline YouTube if available, otherwise direct fngg link 🎬 |
| `cx!fn shop` | `fn tienda` | Fortnite-API | Daily Fortnite item shop (in Spanish) 🛒 |
| `cx!teto` | — | — | 🥖 |

---

## 🛡️ Moderation

| Command | Aliases | Description |
|---|---|---|
| `cx!purge N` | — | Delete N messages (1–100, requires `manage_messages`) |
| `cx!purge all` | — | Wipe the channel in batches (max 100, **asks you to type `confirmar`**) |
| `cx!ruleta` | `ruleta_rusa` | Random voice channel kick (1h cooldown) |
| `cx!angelguard` | — | Emergency: remove all active timeouts on the server |

---

## 👑 Admin Commands

Restricted to `ADMIN_ID` (they fail silently for everyone else).

| Command | Aliases | Description |
|---|---|---|
| `cx!decir <text>` | `say` | Teto speaks in the current channel |
| `cx!dm @user <text>` | `md`, `mensajedirecto` | Send a private message to a user |
| `cx!anuncio <text>` | `announce`, `avisar` | Post a formatted announcement |
| `cx!giveaura @user <amount>` | `daraura`, `regalaraura` | Give or remove (negative) aura |
| `cx!setaura @user <value>` | — | Set a user's aura to a specific value |
| `cx!resetaura @user` | — | Reset a user's aura |
| `cx!muteall` | — | Mute everyone in your voice channel |
| `cx!unmuteall` | — | Unmute everyone in your voice channel |
| `cx!slowmode #channel <seconds>` | `sm` | Set text-channel slowmode (0–21600s) |
| `cx!backup` | `exportar`, `respaldar` | Export all bot data to JSON |
| `cx!stats` | `botinfo` | Full bot dashboard |
| `cx!reload [cog]` | `recargar` | Reload a single cog or all of them |
| `cx!logs [N=15]` | `log` | Show the last N log lines (max 40) |
| `cx!blacklist @user` | `bl` | Block a user from using any command |
| `cx!unblacklist @user` | `unbl` | Unblock a user |
| `cx!blacklistlist` | `bllist` | List blocked users |
| `cx!maintenance` | `mantenimiento` | Toggle maintenance mode |
| `cx!maintenance_status` | `mantstatus` | Show maintenance mode state |
| `cx!vckick [@user]` | `vcsoftban` | Toggle a user on/off the voice ban list (auto-kick on voice join) |
| `cx!teamo` | — | 💕 (secret, creator only) |

---

## 🛰️ Background Systems

| System | Description |
|---|---|
| **💘 Persistent Ship** | Love compatibility % between two users is saved forever. |
| **👢 Voice Ban** | Users on the voice ban list are automatically kicked from any voice channel they join. |
| **🚫 Blacklist** | Blocked users can't run any command (admin exempt). |
| **⚙️ Maintenance** | In maintenance mode only the admin can use commands; others get a notice. |

---

## 📁 Persistent Data

All state lives in JSON files under `PyArchives/` (atomic writes + legacy format migration):

| File | Contents |
|---|---|
| `aura_data.json` | Daily aura per user |
| `ship_data.json` | Compatibility % per couple |
| `blacklist.json` | Blocked user IDs |
| `vcban.json` | Voice ban list (auto-kick on voice join) |
| `maintenance.json` | Maintenance mode flag |
| `backups/` | Snapshots exported via `cx!backup` |

Corrupt files never crash the bot: they are set aside as `.corrupt` and defaults are used.

---

## 🗂️ Project Structure

```
PyArchives/
├── main.py            # Entry point: TetoBot + global check + cog loader
├── config.py          # Re-export of core.settings (backwards compat)
├── core/              # Discord-free nucleus (unit-testable)
│   ├── settings.py    # Validated environment configuration
│   ├── store.py       # Atomic JsonStore with asyncio lock + legacy migration
│   ├── parsing.py     # Durations, picha, ship, formatting, text hygiene
│   ├── fortnite_parse.py  # Pure Fortnite.GG parsers
│   ├── checks.py      # is_admin, cooldown bypass, guild_only
│   ├── embeds.py      # Consistent embed builders
│   └── http.py        # Shared aiohttp client with retries
├── services/
│   └── state.py       # Blacklist, Maintenance, VoiceBan, ShipStore
├── cogs/              # Discord commands (thin layer over core/services)
│   ├── aura.py        # aura, top, bf + aura admin
│   ├── extras.py      # fun: picha, castigo, vs, recordar, hola, de, alaba, teamo
│   ├── admin.py       # owner-only: decir, dm, anuncio, backup, stats, reload, logs, ...
│   ├── utilidad.py    # ping, 8ball, avatar, userinfo, ship, hora, servidor, rol, help, ...
│   ├── moderacion.py  # ruleta, vckick, angelguard, purge
│   ├── apis.py        # pokemon, pais, clima, anime, perro, coctel, espacio, ...
│   ├── fortnite.py    # fn, fn video, fn shop
│   ├── ia.py          # Groq chat
│   └── errores.py     # global error handler
└── utils/             # legacy managers (aura, gifs, dictionary, logger)
tests/                 # pytest: parsing, store, state, aura, fortnite, settings
```

Architecture rule: **testable logic lives in `core/`/`services/`** (never importing `discord`);
cogs are a thin Discord → logic → reply layer.

---

## 🧪 Development & Tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -q   # 44 tests, no token or Discord needed
python -m ruff check PyArchives/core PyArchives/services PyArchives/cogs/aura.py \
    PyArchives/cogs/admin.py PyArchives/cogs/extras.py PyArchives/main.py tests/
python -m py_compile PyArchives/main.py PyArchives/cogs/*.py  # quick smoke
```

---

## 🔐 Security Notes

- **Never commit your `.env`** (it's in `.gitignore`). If a token leaks, **rotate it** in the Discord/Groq portals.
- Admin commands fail silently so they don't leak who the admin is.
- `cx!purge all` asks for confirmation and is capped at 100 messages per batch.
- Text inputs are capped (chat 500, say/DM/announce 1900, searches 80).
- Internal errors go to `PyArchives/logs/bot.log`, never to the channel.

---

## 📱 Contact & Socials

- **X (Twitter):** [@cxctxs_jxck](https://twitter.com/cxctxs_jxck)
- **Instagram:** [@cxctxs_jxck](https://instagram.com/cxctxs_jxck)

---

<div align="center">

**Developed by** `cxctxs_jxck` · **Credits:** Sleepy

*Teto approves this bot. 🥖*

</div>
