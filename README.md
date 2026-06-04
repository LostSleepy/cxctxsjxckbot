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
| `cx!vc @usuario` | `votochopped` | Vota para timeout a alguien (3 votos = 5min) |
| `cx!chat <mensaje>` | `conversar` | Habla con Teto (IA con Groq) |
| `cx!de @usuario` | `dominio` | Expansión de Dominio sobre un objetivo |
| `cx!bf @usuario` | `blackflash` | Black Flash (5% de duplicar aura) |
| `cx!choppeddaily` | `cd`, `chopped`, `dailychopped` | Declara a alguien chopped en anuncios |
| `cx!castigo @usuario` | `cast` | Castigo aleatorio (mute, deaf, kick, timeout) |
| `cx!alaba [@usuario]` | `glaze`, `alabanza`, `cumplido` | Teto halaga a alguien |
| `cx!picha [@usuario]` | `pp` | Medición científica (resultados varían a diario) |
| `cx!ship @u1 [@u2]` | — | Compatibilidad amorosa entre dos usuarios |
| `cx!vs @u1 @u2` | `versus` | Decide quién ganaría en una pelea |
| `cx!8ball [pregunta]` | `pregunta`, `ball` | Consulta la bola 8 mística |
| `cx!elegir [a, b, ...]` | — | Teto elige entre opciones |
| `cx!hola [@usuario]` | `hello`, `hi` | Saludo personalizado con GIF |

---

## ✨ Sistema de Aura

Tu puntuación de aura se reinicia cada 24 horas con un nuevo valor aleatorio (-1000 a 5000).

- **`cx!aura`** — Consulta tu aura del día
- **`cx!top`** — Ranking top 10 del servidor
- **`cx!bf @usuario`** — Un Black Flash tiene 5% de probabilidad de duplicar tu aura
- **`cx!vc @usuario`** — Vota para chopped: 3 votos en 5 min = timeout de 5 min

---

## 🤖 Chat con IA

Teto usa **Groq AI (Llama 3.1 8B / 70B)** para conversar en español.

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!chat <mensaje>` | `conversar` | Habla con Teto con su personalidad única |

*Cooldown de 3s entre mensajes IA.*

---

## 🛠️ Utilidad

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!help` | — | Muestra el panel de comandos |
| `cx!ping` | — | Latencia del bot y tiempo de respuesta de la API |
| `cx!uptime` | — | Cuánto tiempo lleva Teto despierta |
| `cx!avatar [@usuario]` | `av` | Foto de perfil en alta resolución |
| `cx!userinfo [@usuario]` | `u`, `info` | Estadísticas detalladas del usuario |
| `cx!hora` | — | Reloj mundial — Madrid, Nueva York y Japón |
| `cx!servidor` | `server`, `guild` | Info completa del servidor |
| `cx!rol [@rol]` | `role`, `rolinfo` | Info detallada de un rol |
| `cx!recordar <tiempo> <texto>` | `rem`, `reminder` | Pon un recordatorio (ej: `cx!recordar 10m algo`) |
| `cx!pokemon <nombre>` | `poke`, `pokedex` | Info de un Pokémon (PokeAPI) 🔍 |
| `cx!pais <nombre>` | `country`, `país` | Info de un país (REST Countries) 🌍 |
| `cx!clima <ciudad>` | `weather`, `tiempo` | Clima actual de una ciudad (Open-Meteo) 🌤️ |
| `cx!anime <nombre>` | `mal` | Buscar anime en MyAnimeList 🎬 |
| `cx!perro [raza]` | `dog`, `perrito` | Imagen aleatoria de perro 🐕 |
| `cx!razas` | `breeds` | Lista de razas de perro disponibles 🐕 |
| `cx!coctel <nombre>` | `drink`, `cocktail` | Receta de coctel 🍸 |
| `cx!coctelaleatorio` | `randomdrink` | Coctel aleatorio 🍸 |
| `cx!espacio` | `nasa`, `apod` | Foto astronómica del día (NASA) 🚀 |
| `cx!chiste` | `joke` | Chiste aleatorio en español 😂 |
| `cx!traducir <txt>` | `translate` | Traducir texto a español/u otro idioma 🌐 |
| `cx!receta <nombre>` | `recipe` | Receta de comida con ingredientes 🍳 |
| `cx!catfact` | `gatofact` | Dato curioso sobre gatos 🐱 |
| `cx!teto` | — | 🥖 |

---

## 🛡️ Moderación

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!purge [N \| all]` | — | Limpieza masiva de mensajes (requiere manage_messages) |
| `cx!ruleta` | `ruleta_rusa` | Kick aleatorio del canal de voz (cooldown 1h) |
| `cx!angelguard` | — | Emergencia: levanta todos los timeouts del servidor |

---

## 👑 Comandos de Admin

Restringidos al creador del bot.

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!decir <texto>` | `say` | Teto habla en el canal actual |
| `cx!dm @usuario <texto>` | `md`, `mensajedirecto` | Envía un mensaje privado a un usuario |
| `cx!anuncio <texto>` | `announce`, `avisar` | Publica un anuncio en el canal de anuncios |
| `cx!giveaura @usuario <cantidad>` | `daraura` | Da o quita aura a un usuario |
| `cx!setaura @usuario <valor>` | — | Establece el aura de un usuario a un valor específico |
| `cx!resetaura @usuario` | — | Resetea el aura de un usuario |
| `cx!muteall` | — | Silencia a todos en tu canal de voz |
| `cx!unmuteall` | — | Quita el silencio a todos en tu canal de voz |
| `cx!backup` | `exportar`, `respaldar` | Exporta todos los datos del bot a JSON |
| `cx!teamo` | — | 💕 (secreto, solo para el creador) |

---

## 🛰️ Sistemas Automáticos

| Sistema | Descripción |
|---|---|
| **💀 Chopped Diario** | Cada 6 horas, Teto elige un miembro aleatorio y lo declara chopped en anuncios |
| **💘 Ship Persistente** | El % de compatibilidad amorosa entre dos usuarios se guarda para siempre |

---

## ⚙️ Configuración

El bot se configura mediante variables de entorno y `config.py`:

| Variable | Por defecto | Descripción |
|---|---|---|
| `DISCORD_TOKEN` | — | Token del bot de Discord (requerido) |
| `COMMAND_PREFIX` | `cx!` | Prefijo de comandos del bot |
| `GROQ_API_KEY` | — | API Key de Groq para el chat IA |
| `ADMIN_ID` | `979869404110159912` | ID de Discord del creador del bot |

---

## 📱 Contacto y Redes

- **X (Twitter):** [@cxctxs_jxck](https://twitter.com/cxctxs_jxck)
- **Instagram:** [@cxctxs_jxck](https://instagram.com/cxctxs_jxck)

---

<div align="center">

**Desarrollado por** `cxctxs_jxck` · **Créditos:** Sleepy

*Teto aprueba este bot. 🥖*

</div>
