<div align="center">

# 🥖 Teto — Discord Bot

> *"Baked with love. Deployed with intent."*

**A multi-functional Discord bot inspired by Kasane Teto.**
Moderation, entertainment, AI chat, aura system, and a daily dose of chaos.

[![Prefix](https://img.shields.io/badge/Prefix-cx!-ff69b4?style=for-the-badge&logo=discord&logoColor=white)](.)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](.)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=for-the-badge&logo=discord&logoColor=white)](.)

---

🇪🇸 [Versión en Español](README.md)

</div>

---

## 🎮 Fun

| Command | Aliases | Description |
|---|---|---|
| `cx!aura [@user]` | — | Check your daily aura score (resets every 24h) |
| `cx!top` | `ranking`, `leaderboard` | Server aura ranking (top 10) |
| `cx!chat <message>` | `conversar` | Chat with Teto (Groq AI) |
| `cx!de @user` | — | Domain Expansion on a target |
| `cx!bf @user` | `blackflash` | Black Flash (5% chance to double your aura + announcement) |
| `cx!castigo @user` | `cast` | Random punishment (mute / deaf / kick / timeout) — 1h cooldown |
| `cx!alaba [@user]` | `glaze` | Teto praises someone |
| `cx!picha [@user]` | `pp` | Scientific measurement — results vary daily |
| `cx!ship @u1 [@u2]` | — | Love compatibility between two users (persistent) |
| `cx!vs @u1 @u2` | `versus` | Decide who would win in a fight |
| `cx!8ball <question>` | `ball` | Consult the mystical 8ball |
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

*3s cooldown between AI messages.*

---

## 🛠️ Utility

| Command | Aliases | Description |
|---|---|---|
| `cx!help` | — | Show the command panel |
| `cx!ping` | — | Check bot latency and API response time |
| `cx!uptime` | — | How long Teto has been awake |
| `cx!avatar [@user]` | `av` | Profile picture in high resolution |
| `cx!userinfo [@user]` | `user`, `info`, `u` | Detailed user stats (admin can add `raw` for extra info) |
| `cx!hora` | — | World clock — Madrid, New York, Japan |
| `cx!servidor` | `server`, `serverinfo`, `guild`, `guildinfo` | Full server information |
| `cx!rol [@role]` | `role`, `roleinfo` | Detailed role information |
| `cx!recordar <time> <text>` | `rem`, `reminder` | Set a reminder (e.g. `cx!recordar 10m walk the dog`) |

---

## 🌐 APIs & Search

| Command | Aliases | API | Description |
|---|---|---|---|
| `cx!pokemon <name>` | `poke`, `pokedex` | PokeAPI | Pokémon info: Spanish types, stats, sprite 🔍 |
| `cx!pais <name>` | `country` | REST Countries | Country info (capital, population, currency, timezones) 🌍 |
| `cx!clima <city>` | `weather` | Open-Meteo | Current weather for a city 🌤️ |
| `cx!anime <name>` | `mal`, `myanimelist` | Jikan (MAL) | Search anime on MyAnimeList 🎬 |
| `cx!perro [breed]` | `dog`, `doggo` | Dog CEO | Random dog image 🐕 |
| `cx!razas` | `breeds` | Dog CEO | List all available dog breeds 🐕 |
| `cx!coctel <name>` | `cocktail`, `drink` | TheCocktailDB | Cocktail recipe with ingredients 🍸 |
| `cx!coctelaleatorio` | `randomdrink` | TheCocktailDB | Random cocktail recipe 🍸 |
| `cx!espacio` | `space`, `nasa`, `apod` | NASA APOD | Astronomy Picture of the Day 🚀 |
| `cx!chiste` | `joke` | JokeAPI (es) | Random joke in Spanish 😂 |
| `cx!traducir <text>` | `translate`, `trad` | MyMemory | Translate text. Use `cx!traducir en\|hello` to force language 🌐 |
| `cx!receta <name>` | `recipe` | TheMealDB | Food recipe with ingredients 🍳 |
| `cx!catfact` | — | Cat Facts | Random cat fact 🐱 |
| `cx!definir <word>` | `dict` | FreeDictionaryAPI | Word definition lookup (ES → EN fallback) 📖 |
| `cx!teto` | — | — | 🥖 |

---

## 🛡️ Moderation

| Command | Aliases | Description |
|---|---|---|
| `cx!purge [N \| all]` | — | Bulk message purge (requires `manage_messages`) |
| `cx!ruleta` | `ruleta_rusa` | Random voice channel kick (1h cooldown) |
| `cx!angelguard` | — | Emergency: remove all active timeouts on the server |

---

## 👑 Admin Commands

Restricted to `ADMIN_ID`.

| Command | Aliases | Description |
|---|---|---|
| `cx!decir <text>` | `say` | Teto speaks in the current channel |
| `cx!dm @user <text>` | `md` | Send a private message to a user |
| `cx!anuncio <text>` | `announce` | Post a formatted announcement |
| `cx!giveaura @user <amount>` | — | Give or remove (negative) aura from a user |
| `cx!setaura @user <value>` | — | Set a user's aura to a specific value |
| `cx!resetaura @user` | — | Reset a user's aura |
| `cx!muteall` | — | Mute everyone in your voice channel |
| `cx!unmuteall` | — | Unmute everyone in your voice channel |
| `cx!slowmode #channel <seconds>` | `sm` | Set text-channel slowmode (0–21600s, 0 disables) |
| `cx!backup` | — | Export all bot data to JSON |
| `cx!stats` | `botinfo` | Full bot dashboard |
| `cx!reload [cog]` | — | Reload a single cog or all of them |
| `cx!logs [N=15]` | `log` | Show the last N lines of the bot log |
| `cx!blacklist @user` | `bl` | Block a user from using any command |
| `cx!unblacklist @user` | `unbl` | Unblock a user |
| `cx!blacklistlist` | `bllist` | List blocked users |
| `cx!maintenance` | — | Toggle maintenance mode |
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

## ⚙️ Configuration

Configured via environment variables and `config.py`:

| Variable | Default | Description |
|---|---|---|
| `DISCORD_TOKEN` | — | Discord bot token (required) |
| `COMMAND_PREFIX` | `cx!` | Bot command prefix |
| `GROQ_API_KEY` | — | Groq API key for AI chat |
| `ADMIN_ID` | `979869404110159912` | Bot creator's Discord user ID |
| `CANAL_ANUNCIOS_ID` | `1497645495051354113` | Announcements channel |
| `CANAL_BOT_ID` | `1432506760698003466` | Internal bot channel |
| `PORT` | `8080` | Flask keep-alive port |

---

## 📁 Persistent Data

All state lives in JSON files under `PyArchives/`:

| File | Contents |
|---|---|
| `aura_data.json` | Daily aura per user |
| `ship_data.json` | Compatibility % per couple |
| `blacklist.json` | Blocked user IDs |
| `vcban.json` | Voice ban list (auto-kick on voice join) |
| `maintenance.json` | Maintenance mode flag |
| `backups/` | Snapshots exported via `cx!backup` |

---

## 📱 Contact & Socials

- **X (Twitter):** [@cxctxs_jxck](https://twitter.com/cxctxs_jxck)
- **Instagram:** [@cxctxs_jxck](https://instagram.com/cxctxs_jxck)

---

<div align="center">

**Developed by** `cxctxs_jxck` · **Credits:** Sleepy

*Teto approves this bot. 🥖*

</div>
