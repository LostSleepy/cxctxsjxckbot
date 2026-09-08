<div align="center">

# 🥖 Teto — Bot de Discord

> *"Horneada con cariño. Desplegada con intención."*

**Un bot de Discord multifuncional inspirado en Kasane Teto.**
Moderación, entretenimiento, chat con IA, sistema de aura y caos diario garantizado.

[![Prefijo](https://img.shields.io/badge/Prefijo-cx!-ff69b4?style=for-the-badge&logo=discord&logoColor=white)](.)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](.)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=for-the-badge&logo=discord&logoColor=white)](.)

---

🇬🇧 [English Version](README_EN.md)

</div>

---

## 🚀 Instalación

Requisitos: **Python 3.11+**.

```bash
git clone <tu-repo>
cd cxctxsjxckbot

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # y rellena tus claves
```

## ▶️ Ejecución

```bash
python PyArchives/main.py
```

El bot carga los 9 cogs, arranca el servidor de keep-alive (si `ENABLE_WEB=1`)
y se conecta a Discord. Sin `DISCORD_TOKEN` no arranca (falla con mensaje claro).

## ⚙️ Configuración

Toda la configuración vive en variables de entorno (ver `.env.example`).
`PyArchives/core/settings.py` las valida: un valor inválido **no tumba el bot**,
usa el valor por defecto y lo avisa en el log.

| Variable | Por defecto | Descripción |
|---|---|---|
| `DISCORD_TOKEN` | — | Token del bot de Discord (requerido) |
| `GROQ_API_KEY` | — | API Key de Groq para el chat IA (requerido para `cx!chat`) |
| `COMMAND_PREFIX` | `cx!` | Prefijo de comandos |
| `ADMIN_ID` | `979869404110159912` | ID del creador: bypass de cooldowns, blacklist y mantenimiento |
| `CANAL_ANUNCIOS_ID` | `1497645495051354113` | Canal de anuncios y récords de Black Flash (`0` = desactivado) |
| `CANAL_BOT_ID` | `1432506760698003466` | Canal interno (informativo) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Modelo de Groq |
| `GROQ_MAX_TOKENS` | `200` | Máx. tokens por respuesta (16–1024) |
| `ENABLE_WEB` | `1` | Servidor keep-alive para hosting gratuito (`0` = desactivado) |
| `PORT` | `8080` | Puerto del servidor web |

---

## 🎮 Diversión

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!aura [@usuario]` | — | Consulta tu aura del día (se resetea cada 24h) |
| `cx!top` | `ranking`, `leaderboard` | Top 10 de aura del servidor |
| `cx!chat <mensaje>` | `conversar` | Habla con Teto (IA con Groq, máx. 500 caracteres) |
| `cx!de @usuario` | `dominio` | Expansión de Dominio sobre un objetivo |
| `cx!bf @usuario` | `blackflash` | Black Flash (5% de probabilidad de duplicar aura) |
| `cx!castigo @usuario` | `cast` | Castigo aleatorio (mute / deaf / kick / timeout) — cooldown 1h |
| `cx!alaba [@usuario]` | `glaze`, `alabanza`, `cumplido` | Teto halaga a alguien |
| `cx!picha [@usuario]` | `pp` | Medición científica (resultados varían a diario) |
| `cx!ship @u1 [@u2]` | — | Compatibilidad amorosa entre dos usuarios (persistente) |
| `cx!vs @u1 @u2` | `versus` | Decide quién ganaría en una pelea |
| `cx!8ball <pregunta>` | `pregunta`, `ball` | Consulta la bola 8 mística |
| `cx!elegir <opciones>` | — | Teto elige entre opciones separadas por comas |
| `cx!hola` | `hello`, `hi` | Saludo personalizado con GIF |

---

## ✨ Sistema de Aura

Tu puntuación de aura se reinicia cada 24 horas con un nuevo valor aleatorio (-1000 a 5000).

- **`cx!aura`** — Consulta tu aura del día.
- **`cx!top`** — Ranking top 10 del servidor.
- **`cx!bf @usuario`** — Un Black Flash tiene 5% de probabilidad de duplicar tu aura y anunciarlo.

---

## 🤖 Chat con IA

Teto usa **Groq AI (Llama 3.3 70B Versatile)** para conversar en español.

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!chat <mensaje>` | `conversar` | Habla con Teto con su personalidad única |

*Cooldown de 3s entre mensajes de IA. Sin `GROQ_API_KEY` el comando avisa que la IA no está disponible.*

---

## 🛠️ Utilidad

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!help` | — | Muestra el panel de comandos |
| `cx!ping` | — | Latencia del bot y tiempo de respuesta de la API |
| `cx!uptime` | — | Cuánto tiempo lleva Teto despierta |
| `cx!avatar [@usuario]` | `av` | Foto de perfil en alta resolución |
| `cx!userinfo [@usuario]` | `user`, `info`, `u` | Estadísticas detalladas del usuario (admin puede añadir `raw` para info extra) |
| `cx!hora` | — | Reloj mundial — Madrid, Nueva York y Japón |
| `cx!servidor` | `server`, `serverinfo`, `guild`, `guildinfo` | Info completa del servidor |
| `cx!rol [@rol]` | `role`, `roleinfo`, `rolinfo` | Info detallada de un rol |
| `cx!recordar <tiempo> <texto>` | `rem`, `reminder` | Recordatorio: `30s`, `10m`, `2h`, `1d` (máx. 24h). Ej: `cx!recordar 10m sacar al perro` |

---

## 🌐 APIs y búsquedas

| Comando | Aliases | API | Descripción |
|---|---|---|---|
| `cx!pokemon <nombre>` | `poke`, `pokedex` | PokeAPI | Info de un Pokémon con tipos en español, stats y sprite 🔍 |
| `cx!pais <nombre>` | `country`, `país`, `paises` | REST Countries | Info de un país (capital, población, moneda, zonas horarias) 🌍 |
| `cx!clima <ciudad>` | `weather`, `tiempo` | Open-Meteo | Clima actual de una ciudad 🌤️ |
| `cx!anime <nombre>` | `mal`, `myanimelist` | Jikan (MAL) | Buscar anime en MyAnimeList 🎬 |
| `cx!perro [raza]` | `dog`, `perrito`, `doggo` | Dog CEO | Imagen aleatoria de perro 🐕 |
| `cx!razas` | `breeds` | Dog CEO | Lista todas las razas de perro disponibles 🐕 |
| `cx!coctel <nombre>` | `cocktail`, `coctail`, `drink` | TheCocktailDB | Receta de coctel con ingredientes 🍸 |
| `cx!coctelaleatorio` | `randomdrink`, `randomcoctel` | TheCocktailDB | Coctel aleatorio 🍸 |
| `cx!espacio` | `space`, `nasa`, `apod` | NASA APOD | Foto astronómica del día 🚀 |
| `cx!chiste` | `joke`, `chistes` | JokeAPI (es) | Chiste aleatorio en español 😂 |
| `cx!traducir <texto>` | `translate`, `trad` | MyMemory | Traduce texto. Usa `cx!traducir en\|hola` para fijar idioma 🌐 |
| `cx!receta <nombre>` | `recipe`, `comida` | TheMealDB | Receta de comida con ingredientes 🍳 |
| `cx!catfact` | `gatofact`, `factcat` | Cat Facts | Dato curioso aleatorio sobre gatos 🐱 |
| `cx!definir <palabra>` | `define`, `dict` | FreeDictionaryAPI | Definición de una palabra (ES → EN fallback) 📖 |
| `cx!fn <nombre>` | `fortnite` | Fortnite-API + Fortnite.GG | Ficha de cosmético estilo Fortnite.GG: imagen, precio, origen, wishlists, rating y enlace al baile 🎮 |
| `cx!fn video <nombre>` | `fn v` | Fortnite-API + Fortnite.GG | Vídeo del baile: YouTube inline si existe, si no enlace directo de fngg 🎬 |
| `cx!fn shop` | `fn tienda` | Fortnite-API | Tienda diaria de Fortnite en español 🛒 |
| `cx!teto` | — | — | 🥖 |

---

## 🛡️ Moderación

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!purge N` | — | Borra N mensajes (1–100, requiere `manage_messages`) |
| `cx!purge all` | — | Borra el canal por tandas (máx. 100, **pide escribir `confirmar`**) |
| `cx!ruleta` | `ruleta_rusa` | Kick aleatorio del canal de voz (cooldown 1h) |
| `cx!angelguard` | — | Emergencia: levanta todos los timeouts del servidor |

---

## 👑 Comandos de Admin

Restringidos a `ADMIN_ID` (fallan en silencio para el resto).

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!decir <texto>` | `say` | Teto habla en el canal actual |
| `cx!dm @usuario <texto>` | `md`, `mensajedirecto` | Envía un mensaje privado a un usuario |
| `cx!anuncio <texto>` | `announce`, `avisar` | Publica un anuncio formateado en el canal de anuncios |
| `cx!giveaura @usuario <cantidad>` | `daraura`, `regalaraura` | Da o quita aura (negativo) a un usuario |
| `cx!setaura @usuario <valor>` | — | Establece el aura a un valor específico |
| `cx!resetaura @usuario` | — | Resetea el aura de un usuario |
| `cx!muteall` | — | Silencia a todos en tu canal de voz |
| `cx!unmuteall` | — | Quita el silencio a todos en tu canal de voz |
| `cx!slowmode #canal <segundos>` | `sm` | Ajusta el slowmode de un canal de texto (0–21600s) |
| `cx!backup` | `exportar`, `respaldar` | Exporta todos los datos del bot a JSON |
| `cx!stats` | `botinfo` | Dashboard completo del estado del bot |
| `cx!reload [cog]` | `recargar` | Recarga un cog concreto o todos |
| `cx!logs [N=15]` | `log` | Muestra las últimas líneas del log (máx. 40) |
| `cx!blacklist @usuario` | `bl` | Bloquea a un usuario de usar todos los comandos |
| `cx!unblacklist @usuario` | `unbl` | Desbloquea a un usuario |
| `cx!blacklistlist` | `bllist` | Lista usuarios bloqueados |
| `cx!maintenance` | `mantenimiento` | Activa/desactiva el modo mantenimiento |
| `cx!maintenance_status` | `mantstatus` | Consulta el estado del modo mantenimiento |
| `cx!vckick [@usuario]` | `vcsoftban` | Añade/quita un usuario de la lista de voice ban (auto-expulsión al entrar a llamada) |
| `cx!teamo` | — | 💕 (secreto, solo para el creador) |

---

## 🛰️ Sistemas Automáticos

| Sistema | Descripción |
|---|---|
| **💘 Ship Persistente** | El % de compatibilidad amorosa entre dos usuarios se guarda para siempre. |
| **👢 Voice Ban** | Usuarios en la voice ban list son expulsados automáticamente al entrar a cualquier canal de voz. |
| **🚫 Blacklist** | Usuarios bloqueados no pueden ejecutar comandos (admin exento). |
| **⚙️ Mantenimiento** | En modo mantenimiento, solo el admin puede usar comandos; el resto recibe un aviso. |

---

## 📁 Datos Persistentes

El bot guarda todo en JSON dentro de `PyArchives/` (escrituras atómicas + migración de formatos antiguos):

| Archivo | Contiene |
|---|---|
| `aura_data.json` | Aura diaria por usuario |
| `ship_data.json` | % de compatibilidad por pareja |
| `blacklist.json` | Usuarios bloqueados |
| `vcban.json` | Voice ban list (auto-kick en llamada) |
| `maintenance.json` | Estado del modo mantenimiento |
| `backups/` | Snapshots exportados con `cx!backup` |

Los ficheros corruptos no tumban el bot: se apartan como `.corrupt` y se usan valores por defecto.

---

## 🗂️ Estructura del Proyecto

```
PyArchives/
├── main.py            # Punto de entrada: TetoBot + check global + carga de cogs
├── config.py          # Re-export de core.settings (compatibilidad)
├── core/              # Núcleo sin dependencia de Discord (testeable)
│   ├── settings.py    # Configuración validada desde entorno
│   ├── store.py       # JsonStore atómico con lock asyncio + migración legacy
│   ├── parsing.py     # Duraciones, picha, ship, formatos, higiene de texto
│   ├── fortnite_parse.py  # Parsers puros de Fortnite.GG
│   ├── checks.py      # is_admin, bypass de cooldown, guild_only
│   ├── embeds.py      # Constructores de embeds con estilo consistente
│   └── http.py        # Cliente aiohttp compartido con reintentos
├── services/
│   └── state.py       # Blacklist, Maintenance, VoiceBan, ShipStore
├── cogs/              # Comandos Discord (capa fina sobre core/services)
│   ├── aura.py        # aura, top, bf + admin de aura
│   ├── extras.py      # diversión: picha, castigo, vs, recordar, hola, de, alaba, teamo
│   ├── admin.py       # solo dueño: decir, dm, anuncio, backup, stats, reload, logs, ...
│   ├── utilidad.py    # ping, 8ball, avatar, userinfo, ship, hora, servidor, rol, help, ...
│   ├── moderacion.py  # ruleta, vckick, angelguard, purge
│   ├── apis.py        # pokemon, pais, clima, anime, perro, coctel, espacio, ...
│   ├── fortnite.py    # fn, fn video, fn shop
│   ├── ia.py          # chat con Groq
│   └── errores.py     # manejador global de errores
└── utils/             # managers legacy (aura, gifs, diccionario, logger)
tests/                 # pytest: parsing, store, estado, aura, fortnite, settings
```

Regla de arquitectura: **la lógica testeable vive en `core/`/`services/`** (sin importar `discord`);
los cogs son capa fina Discord → lógica → respuesta.

---

## 🧪 Desarrollo y Tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -q   # 44 tests, sin necesidad de token ni de Discord
python -m ruff check PyArchives/core PyArchives/services PyArchives/cogs/aura.py \
    PyArchives/cogs/admin.py PyArchives/cogs/extras.py PyArchives/main.py tests/
python -m py_compile PyArchives/main.py PyArchives/cogs/*.py  # humo rápido
```

---

## 🔐 Notas de Seguridad

- **Nunca subas tu `.env`** (está en `.gitignore`). Si un token se expone, **rotalo** en el portal de Discord/Groq.
- Los comandos de admin fallan en silencio para no filtrar quién es admin.
- `cx!purge all` pide confirmación y está topado a 100 mensajes por tanda.
- Las entradas de texto están topadas (chat 500, decir/DM/anuncio 1900, búsquedas 80).
- Los errores internos se registran en `PyArchives/logs/bot.log`, nunca se envían al canal.

---

## 📱 Contacto y Redes

- **X (Twitter):** [@cxctxs_jxck](https://twitter.com/cxctxs_jxck)
- **Instagram:** [@cxctxs_jxck](https://instagram.com/cxctxs_jxck)

---

<div align="center">

**Desarrollado por** `cxctxs_jxck` · **Créditos:** Sleepy

*Teto aprueba este bot. 🥖*

</div>
