<div align="center">

# 🥖 Teto — Sukuna's Vessel

> *"Baked with cursed energy. Deployed with questionable intent."*

**A multi-functional Discord bot inspired by Jujutsu Kaisen and Kasane Teto.**
Moderation, entertainment, AI chat, intelligent voice monitoring, and a daily dose of chaos.

[![Prefix](https://img.shields.io/badge/Prefix-cx!-ff69b4?style=for-the-badge&logo=discord&logoColor=white)](.)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](.)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=for-the-badge&logo=discord&logoColor=white)](.)

---

🇪🇸 [Versión en Español](README.md)

</div>

---

## 🤖 AI Commands

Teto uses **Groq AI (Llama 3.1 8B)** for intelligent natural language responses in Spanish.
All AI commands must be invoked explicitly — the AI **never responds automatically** to mentions.

### 💬 Chat & Quotes

| Command | Aliases | Description |
|---|---|---|
| `cx!chat <message>` | `conversar` | Chat with Teto (free AI) |
| `cx!frase <topic>` | — | Quote or phrase about a topic |
| `cx!idea` | — | Idea on a topic |
| `cx!inspirar` | `inspo`, `motivar` | Inspirational quote |
| `cx!excusa [reason]` | — | Creative excuse |
| `cx!debate` | `discute`, `preguntai` | Hypothetical question to debate |

### 🎨 Creativity

| Command | Aliases | Description |
|---|---|---|
| `cx!chiste [topic]` | — | Joke about a topic |
| `cx!poema <topic>` | — | Short 2-3 verse poem |
| `cx!cuento [topic]` | — | Micro-story in 3 sentences |
| `cx!citaanime` | `animequote` | Anime quote with character name |
| `cx!nick <name>` | — | 3 nicknames from a name |
| `cx!titulo <topic>` | — | Invented movie/series title with genre |
| `cx!escenario [context]` | — | Hypothetical scenario |

### 💘 Social Interaction

| Command | Aliases | Description |
|---|---|---|
| `cx!shipp @u1 @u2` | — | Ship name + description + % compatibility |
| `cx!bromai @user` | `broma`, `insultoia` | Playful insult |
| `cx!halago @user` | `piropo`, `cumplidoia` | Sincere compliment |
| `cx!retar @user` | `reto` | Launch a challenge at someone |
| `cx!futuro @user` | — | Future prediction |

### 🔮 Divination & Advice

| Command | Aliases | Description |
|---|---|---|
| `cx!horoscopo [sign]` | `horo` | Horoscope for a sign |
| `cx!consejo [topic]` | — | Useful advice |
| `cx!elige <opt1> o <opt2>` | — | AI chooses between options |

### 📚 Utility & Knowledge

| Command | Aliases | Description |
|---|---|---|
| `cx!traducir <text>` | `translate`, `trad` | Translate text |
| `cx!resumir <text>` | `resumen`, `summary` | Summarize text |
| `cx!definir <word>` | — | Real definition of a word |
| `cx!sinonimo <word>` | `sinonimos` | Synonyms for a word |
| `cx!explica <concept>` | — | Explain concept simply |
| `cx!toplista <topic> [n]` | `toplist`, `rankia` | Top N list about a topic |
| `cx!tipoprogramacion [topic]` | `devtip`, `prog` | Programming tip |
| `cx!curiosidad` | `dato` | Curious fact |

### 🎮 Entertainment

| Command | Aliases | Description |
|---|---|---|
| `cx!quehago` | `aburrido`, `hacer` | Suggests something to do |

### 🤖 Meta

| Command | Aliases | Description |
|---|---|---|
| `cx!personalidad` | — | Teto describes herself |
| `cx!version` | `versión` | Bot version and info |
| `cx!error` | `fallo`, `panic` | Fake system error |

**Note:** Each command has its own tailored AI prompt. 3s cooldown between AI commands.

---

## 🥖 Utility

| Command | Aliases | Description |
|---|---|---|
| `cx!help` | — | Show the command panel |
| `cx!ping` | — | Check bot latency and API response time |
| `cx!uptime` | — | Show how long the bot has been running |
| `cx!avatar [@user]` | `av` | View any member's profile picture in high resolution |
| `cx!userinfo [@user]` | `user`, `info`, `u` | Detailed user stats: roles, join date, account age |
| `cx!aleatorio` | `azar`, `random_user` | Pick a random server member |
| `cx!elegir [a, b, ...]` | — | Can't decide? Let Teto choose for you |
| `cx!8ball [question]` | `pregunta`, `ball` | Consult the mystical 8ball about your fate |
| `cx!hora` | — | World clock — Madrid, New York, and Japan |
| `cx!ship @u1 [@u2]` | — | Calculate love compatibility between two users |
| `cx!teto` | — | 🥖 |
| `cx!servidor` | `server`, `serverinfo`, `guild`, `guildinfo` | Full server info: members, channels, boosts, owner |
| `cx!rol [@role]` | `role`, `roleinfo`, `rolinfo` | Detailed role info: color, members, position |
| `cx!emoji [:emoji:]` | `agrandar`, `jumbo`, `emojigrande` | View a custom server emoji in large size |
| `cx!encuesta [question]` | `votacion`, `poll` | Create a poll with ✅/❌ reactions |

---

## ✨ Aura System

Your daily aura score resets every 24 hours with a new random value (-1000 to 5000).

| Command | Aliases | Description |
|---|---|---|
| `cx!aura [@user]` | — | Check your (or someone else's) daily aura score |
| `cx!top` | `ranking`, `leaderboard` | Show the server's aura ranking (top 10) |
| `cx!da @user` | `dueloaura` | Aura duel: winner gets +50, loser gets -100 |
| `cx!robar @user` | `rob` | Attempt to steal aura (50% success rate) |
| `cx!picha [@user]` | `pp` | Scientific measurement. Results vary daily. |
| `cx!vc @user` | `votochopped` | Vote to chopped someone (3 votes = 5min timeout) |
| `cx!choppeddaily` | `cd`, `chopped`, `dailychopped` | Pick a random member and publicly declare them chopped |

### 🛡️ Tips
- Having **✨ glow** in your inventory makes your name sparkle in the ranking
- Use **🛡️ shield** to protect against robberies
- Use **🚀 boost** to double your next aura roll

---

## 🎭 Jujutsu Kaisen

| Command | Aliases | Description |
|---|---|---|
| `cx!de @user` | `dominio` | Execute a Domain Expansion on a target |
| `cx!bf @user` | `blackflash` | Launch a Black Flash (5% chance to double aura) |
| `cx!ritual` | `invocacion`, `invocar` | Random ritual with 10 possible effects on your aura |
| `cx!dedo` | `dedosukuna`, `buscardedo` | Search for a Sukuna finger (30% chance, 10min cooldown) |
| `cx!sukuna` | `dedos`, `misdedos` | Check your Sukuna finger collection |
| `cx!maldicion @user` | `mal`, `maldice` | Curse someone with Jujutsu Kaisen themed curses |
| `cx!alaba [@user]` | `glaze`, `alabanza`, `cumplido` | Teto praises someone with an epic compliment |

### 💀 Sukuna Fingers
Collect all **20 fingers** to become the **King of Curses**. Track your progress with `cx!sukuna` and see the top 3 collectors in the server.

---

## 🛒 Shop & Items

Buy items with aura and use them for special effects.

| Command | Aliases | Description |
|---|---|---|
| `cx!tienda` | `shop`, `mercadillo` | Browse available items |
| `cx!comprar <item>` | `buy`, `adquirir` | Purchase an item with your aura |
| `cx!inventario` | `inv`, `bolsillo` | View your purchased items |
| `cx!usar <item>` | — | Use an item from your inventory |

### Available Items

| Item | ID | Price | Effect |
|---|---|---|---|
| ✨ Aura Glow | `glow` | 500 | Your name sparkles in the ranking (auto) |
| 🔄 Aura Reroll | `skip` | 800 | Reroll your daily aura |
| 🛡️ Aura Shield | `shield` | 600 | Protects you from 1 robbery |
| 🚀 x2 Multiplier | `boost` | 1200 | Your next aura roll is doubled |

---

## 🎲 Games & Fun

| Command | Aliases | Description |
|---|---|---|
| `cx!ppt [move]` | `piedrapapeltijera`, `piedra` | Rock, paper, scissors against Teto (win = aura) |
| `cx!coinflip` | `tirar`, `caraocruz` | Flip a coin |
| `cx!dado [sides]` | `dice`, `d` | Roll a die (defaults to d6) |
| `cx!vs @u1 @u2` | `versus` | Decide who would win in a fight |
| `cx!insultar @user` | `insulto` | Insult someone with style |
| `cx!felicitar @user` | `feli`, `felicitacion` | Congratulate someone warmly |
| `cx!hola [@user]` | `hello`, `hi` | Personalized greeting with random GIFs |
| `cx!recordar <time> <text>` | `reminder`, `rem` | Set a reminder (e.g. `cx!recordar 10m Walk the dog`) |

---

## 🛡️ Moderation

| Command | Aliases | Description |
|---|---|---|
| `cx!ruleta` | `ruleta_rusa` | Random voice channel kick — someone's getting yeeted |
| `cx!angelguard` | — | Emergency: lifts all active timeouts on the server |
| `cx!mlshr [N \| all]` | — | Bulk message purge (requires manage_messages) |

---

## 👑 Admin Commands

Restricted to the bot creator.

| Command | Aliases | Description |
|---|---|---|
| `cx!decir <text>` | `say` | Teto speaks in the current channel |
| `cx!dm @user <text>` | `md`, `mensajedirecto` | Send a private message to a user |
| `cx!anuncio <text>` | `announce`, `avisar` | Post a formatted announcement in the announcements channel |
| `cx!saycanal <#channel> <text>` | `hablar`, `deciren` | Teto speaks in a specific channel |
| `cx!giveaura @user <amount>` | `daraura`, `regalaraura` | Give or remove aura from a user |
| `cx!setaura @user <value>` | — | Set a user's aura to a specific value |
| `cx!resetaura @user` | — | Reset a user's aura |
| `cx!castigo @user` | `cast` | Sentence someone to a random punishment |
| `cx!backup` | `exportar`, `respaldar` | Export all bot data to JSON |
| `cx!cita @u1 @u2` | — | Move two users to the date channel |
| `cx!re <#channel>` | `reunion`, `raid` | Move all voice users to a specified channel |
| `cx!muteall` | — | Mute everyone in your voice channel |
| `cx!unmuteall` | — | Unmute everyone in your voice channel |

---

## 🛰️ Intelligent Systems

The bot runs background systems automatically:

| System | Description |
|---|---|
| **🧲 Date Magnet** | If two configured user IDs are in different voice channels, Teto moves them both to the date channel simultaneously |
| **💀 Chopped Alert** | Every 6 hours, Teto picks a random member and declares them chopped in announcements |
| **🛡️ Restraining Orders** | Prevent two users from being in the same voice channel |

### Voice Monitoring Commands

| Command | Description |
|---|---|
| `cx!nxc` | Toggle the voice monitoring system on/off |
| `cx!oa @u1 @u2` | `ordenalejamiento` — Toggle restraining order between two users |

---

## ⚙️ Configuration

The bot is configured via environment variables and `config.py`:

| Variable | Default | Description |
|---|---|---|
| `DISCORD_TOKEN` | — | Discord bot token (required) |
| `COMMAND_PREFIX` | `cx!` | Bot command prefix |
| `GROQ_API_KEY` | — | Groq API key for AI commands |
| `KLIPY_API_KEY` | — | Klipy API key for GIFs |
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
