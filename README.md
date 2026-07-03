<div align="center">

# 🥖 Teto — Bot de Discord

> *"Horneada con cariño. Desplegada con intención."*

**Un bot de Discord multifuncional inspirado en Kasane Teto.**
Moderación, entretenimiento, chat con IA, sistema de aura y caos diario garantizado.

[![Prefijo](https://img.shields.io/badge/Prefijo-cx!-ff69b4?style=for-the-badge&logo=discord&logoColor=white)](.)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](.)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=for-the-badge&logo=discord&logoColor=white)](.)

---

🇬🇧 [English Version](README_EN.md)

</div>

---

## 🎮 Diversión

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!aura [@usuario]` | — | Consulta tu aura del día (se resetea cada 24h) |
| `cx!top` | `ranking`, `leaderboard` | Top 10 de aura del servidor |
| `cx!chat <mensaje>` | `conversar` | Habla con Teto (IA con Groq) |
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

*Cooldown de 3s entre mensajes de IA.*

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
| `cx!recordar <tiempo> <texto>` | `rem`, `reminder` | Recordatorio (ej: `cx!recordar 10m sacar al perro`) |

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
| `cx!teto` | — | — | 🥖 |

---

## 🛡️ Moderación

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!purge [N \| all]` | — | Limpieza masiva de mensajes (requiere `manage_messages`) |
| `cx!ruleta` | `ruleta_rusa` | Kick aleatorio del canal de voz (cooldown 1h) |
| `cx!angelguard` | — | Emergencia: levanta todos los timeouts del servidor |

---

## 👑 Comandos de Admin

Restringidos a `ADMIN_ID`.

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
| `cx!logs [N=15]` | `log` | Muestra las últimas líneas del log |
| `cx!blacklist @usuario` | `bl` | Bloquea a un usuario de usar todos los comandos |
| `cx!unblacklist @usuario` | `unbl` | Desbloquea a un usuario |
| `cx!blacklistlist` | `bllist` | Lista usuarios bloqueados |
| `cx!maintenance` | `mantenimiento` | Activa/desactiva el modo mantenimiento |
| `cx!maintenance_status` | `mantstatus` | Consulta el estado del modo mantenimiento |
| `cx!teamo` | — | 💕 (secreto, solo para el creador) |

---

## 🛰️ Sistemas Automáticos

| Sistema | Descripción |
|---|---|
| **💘 Ship Persistente** | El % de compatibilidad amorosa entre dos usuarios se guarda para siempre. |
| **🚫 Blacklist** | Usuarios bloqueados no pueden ejecutar comandos (admin exento). |
| **⚙️ Mantenimiento** | En modo mantenimiento, solo el admin puede usar comandos; el resto recibe un aviso. |

---

## ⚙️ Configuración

El bot se configura mediante variables de entorno y `config.py`:

| Variable | Por defecto | Descripción |
|---|---|---|
| `DISCORD_TOKEN` | — | Token del bot de Discord (requerido) |
| `COMMAND_PREFIX` | `cx!` | Prefijo de comandos del bot |
| `GROQ_API_KEY` | — | API Key de Groq para el chat IA |
| `ADMIN_ID` | `979869404110159912` | ID de Discord del creador del bot |
| `CANAL_ANUNCIOS_ID` | `1497645495051354113` | Canal para anuncios |
| `CANAL_BOT_ID` | `1432506760698003466` | Canal interno del bot |
| `PORT` | `8080` | Puerto del servidor Flask (keep-alive) |

---

## 📁 Datos Persistentes

El bot guarda todo en JSON dentro de `PyArchives/`:

| Archivo | Contiene |
|---|---|
| `aura_data.json` | Aura diaria por usuario |
| `ship_data.json` | % de compatibilidad por pareja |
| `blacklist.json` | Usuarios bloqueados |
| `maintenance.json` | Estado del modo mantenimiento |
| `backups/` | Snapshots exportados con `cx!backup` |

---

## 📱 Contacto y Redes

- **X (Twitter):** [@cxctxs_jxck](https://twitter.com/cxctxs_jxck)
- **Instagram:** [@cxctxs_jxck](https://instagram.com/cxctxs_jxck)

---

<div align="center">

**Desarrollado por** `cxctxs_jxck` · **Créditos:** Sleepy

*Teto aprueba este bot. 🥖*

</div>
