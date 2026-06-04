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
| `cx!vc @user` | `votochopped` | Vote to timeout someone (3 votes = 5min) |
| `cx!chat <message>` | `conversar` | Chat with Teto (Groq AI) |
| `cx!de @user` | `dominio` | Domain Expansion on a target |
| `cx!bf @user` | `blackflash` | Black Flash (5% chance to double aura) |
| `cx!choppeddaily` | `cd`, `chopped`, `dailychopped` | Declare someone chopped in announcements |
| `cx!castigo @user` | `cast` | Random punishment (mute, deaf, kick, timeout) |
| `cx!alaba [@user]` | `glaze`, `cumplido` | Teto praises someone with a compliment |
| `cx!picha [@user]` | `pp` | Scientific measurement — results vary daily |
| `cx!ship @u1 [@u2]` | — | Love compatibility between two users |
| `cx!vs @u1 @u2` | `versus` | Decide who would win in a fight |
| `cx!8ball [question]` | `pregunta`, `ball` | Consult the mystical 8ball |
| `cx!elegir [a, b, ...]` | — | Teto chooses between options |
| `cx!hola [@user]` | `hello`, `hi` | Personalized greeting with GIF |

---

## ✨ Aura System

Your daily aura score resets every 24 hours with a new random value (-1000 to 5000).

- **`cx!aura`** — Check your daily aura
- **`cx!top`** — Server top 10 ranking
- **`cx!bf @user`** — Black Flash has a 5% chance to double your aura
- **`cx!vc @user`** — Vote to chopped: 3 votes in 5 min = 5 min timeout

---

## 🤖 AI Chat

Teto uses **Groq AI (Llama 3.1 8B / 70B)** to chat in Spanish.

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
| `cx!userinfo [@user]` | `u`, `info` | Detailed user stats |
| `cx!hora` | — | World clock — Madrid, New York, Japan |
| `cx!servidor` | `server`, `guild` | Full server information |
| `cx!rol [@role]` | `role`, `rolinfo` | Detailed role information |
| `cx!recordar <time> <text>` | `rem`, `reminder` | Set a reminder (e.g. `cx!recordar 10m something`) |
| `cx!pokemon <name>` | `poke`, `pokedex` | Pokemon info (PokeAPI) 🔍 |
| `cx!pais <name>` | `country` | Country info (REST Countries API) 🌍 |
| `cx!clima <city>` | `weather` | Current weather (Open-Meteo API) 🌤️ |
| `cx!anime <name>` | `mal` | Search anime on MyAnimeList 🎬 |
| `cx!perro [breed]` | `dog` | Random dog image 🐕 |
| `cx!razas` | `breeds` | List all available dog breeds 🐕 |
| `cx!cocktail <name>` | `drink` | Cocktail recipe 🍸 |
| `cx!coctelaleatorio` | `randomdrink` | Random cocktail recipe 🍸 |
| `cx!space` | `nasa`, `apod` | NASA Astronomy Picture of the Day 🚀 |
| `cx!chiste` | `joke` | Random joke in Spanish 😂 |
| `cx!traducir <txt>` | `translate` | Translate text to Spanish/other languages 🌐 |
| `cx!receta <name>` | `recipe` | Food recipe with ingredients 🍳 |
| `cx!catfact` | `gatofact` | Random cat fact 🐱 |
| `cx!teto` | — | 🥖 |

---

## 🛡️ Moderation

| Command | Aliases | Description |
|---|---|---|
| `cx!purge [N \| all]` | — | Bulk message purge (requires manage_messages) |
| `cx!ruleta` | `ruleta_rusa` | Random voice channel kick (1h cooldown) |
| `cx!angelguard` | — | Emergency: remove all active timeouts on the server |

---

## 👑 Admin Commands

Restricted to the bot creator.

| Command | Aliases | Description |
|---|---|---|
| `cx!decir <text>` | `say` | Teto speaks in the current channel |
| `cx!dm @user <text>` | `md` | Send a private message to a user |
| `cx!anuncio <text>` | `announce`, `avisar` | Post a formatted announcement |
| `cx!giveaura @user <amount>` | `daraura` | Give or remove aura from a user |
| `cx!setaura @user <value>` | — | Set a user's aura to a specific value |
| `cx!resetaura @user` | — | Reset a user's aura |
| `cx!muteall` | — | Mute everyone in your voice channel |
| `cx!unmuteall` | — | Unmute everyone in your voice channel |
| `cx!backup` | `exportar`, `respaldar` | Export all bot data to JSON |
| `cx!teamo` | — | 💕 (secret, creator only) |

---

## 🛰️ Background Systems

| System | Description |
|---|---|
| **💀 Chopped Daily** | Every 6 hours, Teto picks a random member and declares them chopped in announcements |
| **💘 Persistent Ship** | Love compatibility % between two users is saved forever |

---

## ⚙️ Configuration

The bot is configured via environment variables and `config.py`:

| Variable | Default | Description |
|---|---|---|
| `DISCORD_TOKEN` | — | Discord bot token (required) |
| `COMMAND_PREFIX` | `cx!` | Bot command prefix |
| `GROQ_API_KEY` | — | Groq API key for AI chat |
| `ADMIN_ID` | `979869404110159912` | Bot creator's Discord user ID |

---

## 📱 Contact & Socials

- **X (Twitter):** [@cxctxs_jxck](https://twitter.com/cxctxs_jxck)
- **Instagram:** [@cxctxs_jxck](https://instagram.com/cxctxs_jxck)

---

<div align="center">

**Developed by** `cxctxs_jxck` · **Credits:** Sleepy

*Teto approves this bot. 🥖*

</div>
