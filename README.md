<div align="center">

# 🥖 Teto — El Recipiente de Sukuna

> *"Horneada con energía maldita. Desplegada con intenciones cuestionables."*

**Un bot de Discord multifuncional inspirado en Jujutsu Kaisen y Kasane Teto.**
Moderación, entretenimiento, chat con IA, monitoreo de voz inteligente y caos diario garantizado.

[![Prefijo](https://img.shields.io/badge/Prefijo-cx!-ff69b4?style=for-the-badge&logo=discord&logoColor=white)](.)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](.)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=for-the-badge&logo=discord&logoColor=white)](.)

---

🇬🇧 [English Version](README_EN.md)

</div>

---

## 🤖 Comandos IA

Teto usa **Groq AI (Llama 3.1 8B)** para responder con inteligencia natural en español.
Todos los comandos de IA se invocan explícitamente — la IA **nunca responde automáticamente** a menciones.

### 💬 Chat & Frases

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!chat <mensaje>` | `conversar` | Habla con Teto (IA libre) |
| `cx!frase <tema>` | — | Cita o frase sobre un tema |
| `cx!idea` | — | Idea sobre un tema |
| `cx!inspirar` | `inspo`, `motivar` | Frase de inspiración |
| `cx!excusa [motivo]` | — | Excusa creativa |
| `cx!debate` | `discute`, `preguntai` | Pregunta hipotética para debatir |

### 🎨 Creatividad

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!chiste [tema]` | — | Chiste sobre un tema |
| `cx!poema <tema>` | — | Poema corto de 2-3 versos |
| `cx!cuento [tema]` | — | Microcuento de 3 frases |
| `cx!citaanime` | `animequote` | Cita de anime con personaje |
| `cx!nick <nombre>` | — | 3 apodos a partir de un nombre |
| `cx!titulo <tema>` | — | Título de peli/serie inventado con género |
| `cx!escenario [contexto]` | — | Escenario hipotético |

### 💘 Interacción Social

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!shipp @u1 @u2` | — | Ship name + descripción + % de compatibilidad |
| `cx!bromai @usuario` | `broma`, `insultoia` | Insulto de broma |
| `cx!halago @usuario` | `piropo`, `cumplidoia` | Cumplido sincero |
| `cx!retar @usuario` | `reto` | Lanza un reto a alguien |
| `cx!futuro @usuario` | — | Predicción del futuro |

### 🔮 Adivinación & Consejos

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!horoscopo [signo]` | `horo` | Horóscopo para un signo |
| `cx!consejo [tema]` | — | Consejo útil |
| `cx!elige <op1> o <op2>` | — | IA elige entre opciones |

### 📚 Utilidad & Conocimiento

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!traducir <texto>` | `translate`, `trad` | Traduce texto |
| `cx!resumir <texto>` | `resumen`, `summary` | Resume un texto |
| `cx!definir <palabra>` | — | Definición real de una palabra |
| `cx!sinonimo <palabra>` | `sinonimos` | Sinónimos de una palabra |
| `cx!explica <concepto>` | — | Explica concepto de forma simple |
| `cx!toplista <tema> [n]` | `toplist`, `rankia` | Top N sobre un tema |
| `cx!tipoprogramacion [tema]` | `devtip`, `prog` | Tip de programación |
| `cx!curiosidad` | `dato` | Dato curioso |

### 🎮 Entretenimiento

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!quehago` | `aburrido`, `hacer` | Sugiere algo que hacer |

### 🤖 Meta

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!personalidad` | — | Teto se describe a sí misma |
| `cx!version` | `versión` | Versión e información del bot |
| `cx!error` | `fallo`, `panic` | Error falso del sistema |

**Nota:** Cada comando tiene un prompt de IA específico para su función. Cooldown de 3s entre comandos IA.

---

## 🥖 Utilidad

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!help` | — | Muestra el panel de comandos |
| `cx!ping` | — | Latencia del bot y tiempo de respuesta de la API |
| `cx!uptime` | — | Cuánto tiempo lleva Teto despierta |
| `cx!avatar [@usuario]` | `av` | Foto de perfil de cualquier miembro en alta resolución |
| `cx!userinfo [@usuario]` | `user`, `info`, `u` | Estadísticas detalladas: roles, fecha de unión, antigüedad |
| `cx!aleatorio` | `azar`, `random_user` | Elige un miembro aleatorio del servidor |
| `cx!elegir [a, b, ...]` | — | ¿No puedes decidir? Deja que Teto elija por ti |
| `cx!8ball [pregunta]` | `pregunta`, `ball` | Consulta tu destino con la mística bola 8 |
| `cx!hora` | — | Reloj mundial — Madrid, Nueva York y Japón |
| `cx!ship @u1 [@u2]` | — | Calcula la compatibilidad amorosa entre dos usuarios |
| `cx!teto` | — | 🥖 |
| `cx!servidor` | `server`, `serverinfo`, `guild`, `guildinfo` | Info completa del servidor |
| `cx!rol [@rol]` | `role`, `roleinfo`, `rolinfo` | Info detallada de un rol |
| `cx!emoji [:emoji:]` | `agrandar`, `jumbo`, `emojigrande` | Muestra un emoji personalizado del servidor en grande |
| `cx!encuesta [pregunta]` | `votacion`, `poll` | Crea una votación con reacciones ✅/❌ |

---

## ✨ Sistema de Aura

Tu puntuación de aura diaria se reinicia cada 24 horas con un nuevo valor aleatorio (-1000 a 5000).

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!aura [@usuario]` | — | Consulta tu aura del día (o la de otro) |
| `cx!top` | `ranking`, `leaderboard` | Top 10 de aura del servidor |
| `cx!da @usuario` | `dueloaura` | Duelo de aura: ganador +50, perdedor -100 |
| `cx!robar @usuario` | `rob` | Intenta robar aura (50% de probabilidad) |
| `cx!picha [@usuario]` | `pp` | Medición científica. Los resultados varían a diario. |
| `cx!vc @usuario` | `votochopped` | Vota para hacer chopped a alguien (3 votos = 5min de timeout) |
| `cx!choppeddaily` | `cd`, `chopped`, `dailychopped` | Elige un miembro aleatorio y lo declara chopped públicamente |

### 🛡️ Consejos
- Tener **✨ glow** en tu inventario hace que tu nombre brille en el ranking
- Usa **🛡️ shield** para protegerte de robos
- Usa **🚀 boost** para duplicar tu próxima tirada de aura

---

## 🎭 Jujutsu Kaisen

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!de @usuario` | `dominio` | Ejecuta una Expansión de Dominio sobre un objetivo |
| `cx!bf @usuario` | `blackflash` | Lanza un Destello Negro (5% de probabilidad de duplicar aura) |
| `cx!ritual` | `invocacion`, `invocar` | Ritual aleatorio con 10 efectos posibles en tu aura |
| `cx!dedo` | `dedosukuna`, `buscardedo` | Busca un dedo de Sukuna (30% de probabilidad, 10min de cooldown) |
| `cx!sukuna` | `dedos`, `misdedos` | Revisa tu colección de dedos de Sukuna |
| `cx!maldicion @usuario` | `mal`, `maldice` | Maldice a alguien con maldiciones temáticas de Jujutsu Kaisen |
| `cx!alaba [@usuario]` | `glaze`, `alabanza`, `cumplido` | Teto halaga a alguien con un cumplido épico |

### 💀 Dedos de Sukuna
Colecciona los **20 dedos** para convertirte en el **Rey de las Maldiciones**. Sigue tu progreso con `cx!sukuna` y mira el top 3 de coleccionistas del servidor.

---

## 🛒 Tienda y Objetos

Compra objetos con aura y úsalos para efectos especiales.

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!tienda` | `shop`, `mercadillo` | Explora los objetos disponibles |
| `cx!comprar <item>` | `buy`, `adquirir` | Compra un objeto con tu aura |
| `cx!inventario` | `inv`, `bolsillo` | Revisa tus objetos comprados |
| `cx!usar <item>` | — | Usa un objeto de tu inventario |

### Objetos Disponibles

| Objeto | ID | Precio | Efecto |
|---|---|---|---|
| ✨ Brillo de Aura | `glow` | 500 | Tu nombre brilla en el ranking (automático) |
| 🔄 Reintento de Aura | `skip` | 800 | Vuelve a tirar tu aura diaria |
| 🛡️ Escudo de Aura | `shield` | 600 | Te protege de 1 robo |
| 🚀 Multiplicador x2 | `boost` | 1200 | Tu próxima tirada de aura se duplica |

---

## 🎲 Juegos y Diversión

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!ppt [movimiento]` | `piedrapapeltijera`, `piedra` | Piedra, papel o tijera contra Teto (ganar = aura) |
| `cx!coinflip` | `tirar`, `caraocruz` | Lanza una moneda al aire |
| `cx!dado [lados]` | `dice`, `d` | Tira un dado (por defecto d6) |
| `cx!vs @u1 @u2` | `versus` | Decide quién ganaría en una pelea |
| `cx!insultar @usuario` | `insulto` | Insulta a alguien con ingenio |
| `cx!felicitar @usuario` | `feli`, `felicitacion` | Felicita a alguien con cariño |
| `cx!hola [@usuario]` | `hello`, `hi` | Saludo personalizado con GIFs aleatorios |
| `cx!recordar <tiempo> <texto>` | `reminder`, `rem` | Pon un recordatorio (ej. `cx!recordar 10m Sacar al perro`) |

---

## 🛡️ Moderación

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!ruleta` | `ruleta_rusa` | Kick aleatorio del canal de voz — alguien va a volar |
| `cx!angelguard` | — | Emergencia: levanta todos los timeouts activos del servidor |
| `cx!mlshr [N \| all]` | — | Limpieza masiva de mensajes (requiere manage_messages) |

---

## 👑 Comandos de Admin

Restringidos al creador del bot.

| Comando | Aliases | Descripción |
|---|---|---|
| `cx!decir <texto>` | `say` | Teto habla en el canal actual |
| `cx!dm @usuario <texto>` | `md`, `mensajedirecto` | Envía un mensaje privado a un usuario |
| `cx!anuncio <texto>` | `announce`, `avisar` | Publica un anuncio formateado en el canal de anuncios |
| `cx!saycanal <#canal> <texto>` | `hablar`, `deciren` | Teto habla en un canal específico |
| `cx!giveaura @usuario <cantidad>` | `daraura`, `regalaraura` | Da o quita aura a un usuario |
| `cx!setaura @usuario <valor>` | — | Establece el aura de un usuario a un valor específico |
| `cx!resetaura @usuario` | — | Resetea el aura de un usuario |
| `cx!castigo @usuario` | `cast` | Condena a alguien a un castigo aleatorio |
| `cx!backup` | `exportar`, `respaldar` | Exporta todos los datos del bot a JSON |
| `cx!cita @u1 @u2` | — | Mueve a dos usuarios al canal de citas |
| `cx!re <#canal>` | `reunion`, `raid` | Mueve a todos los usuarios de voz a un canal específico |
| `cx!muteall` | — | Silencia a todos en tu canal de voz |
| `cx!unmuteall` | — | Quita el silencio a todos en tu canal de voz |

---

## 🛰️ Sistemas Inteligentes

El bot ejecuta sistemas automáticos en segundo plano:

| Sistema | Descripción |
|---|---|
| **🧲 Imán de Citas** | Si dos IDs configuradas están en canales de voz distintos, Teto las mueve al canal de citas simultáneamente |
| **💀 Alerta Chopped** | Cada 6 horas, Teto elige un miembro aleatorio y lo declara chopped en anuncios |
| **🛡️ Órdenes de Alejamiento** | Evita que dos usuarios estén en el mismo canal de voz |

### Comandos de Monitoreo de Voz

| Comando | Descripción |
|---|---|
| `cx!nxc` | Activa/desactiva el sistema de monitoreo de voz |
| `cx!oa @u1 @u2` | `ordenalejamiento` — Activa/desactiva orden de alejamiento entre dos usuarios |

---

## ⚙️ Configuración

El bot se configura mediante variables de entorno y `config.py`:

| Variable | Por defecto | Descripción |
|---|---|---|
| `DISCORD_TOKEN` | — | Token del bot de Discord (requerido) |
| `COMMAND_PREFIX` | `cx!` | Prefijo de comandos del bot |
| `GROQ_API_KEY` | — | API Key de Groq para los comandos de IA |
| `KLIPY_API_KEY` | — | API Key de Klipy para los GIFs |
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
