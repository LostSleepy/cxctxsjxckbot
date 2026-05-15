"""
AI cog for the Teto Discord bot.
Responds only via commands — no automatic @mention listening.
Uses Groq API (llama-3.1-8b-instant) for various AI-powered features.
"""
import asyncio
import logging
from typing import Optional

import discord
from discord.ext import commands
from groq import AsyncGroq

from config import GROQ_API_KEY, GROQ_MAX_TOKENS, GROQ_MODEL
from utils.dictionary import lookup_word

log = logging.getLogger(__name__)

# ── System Prompts ────────────────────────────────────────────────────────────
# Each command has its own tailored prompt.
# All prompts are literal and direct — no jokes, no creative embellishments.

PROMPT_TETO: str = (
    "Eres Teto, una chispa inspirada en Kasane Teto (la vocaloid). "
    "Hablas español castellano de forma natural y directa. "
    "Respondes exactamente a lo que te preguntan, sin rodeos, "
    "sin jokes ni comentarios graciosos. "
    "Usa emojis con moderación. Sé concisa: máximo 50 palabras. "
    "Si te preguntan algo, responde con información útil y directa."
)

PROMPT_FRASE: str = (
    "Dado un tema, genera una frase o cita real sobre ese tema. "
    "Debe ser apropiada y directa, sin humor ni sarcasmo. "
    "Máximo 30 palabras. Responde solo con la frase."
)

PROMPT_IDEA: str = (
    "Eres un generador de ideas prácticas. "
    "Genera una idea útil y realista sobre lo que te pidan. "
    "Máximo 30 palabras. Responde solo con la idea."
)

PROMPT_TRADUCIR: str = (
    "Eres un traductor. Traduce el texto al idioma indicado. "
    "Si no especifican idioma, traduce al español. "
    "Responde SOLO con la traducción, sin explicaciones."
)

PROMPT_RESUMIR: str = (
    "Resume el texto dado en español, capturando los puntos clave. "
    "Máximo 3 oraciones. Responde solo con el resumen."
)

PROMPT_CITA_ANIME: str = (
    "Genera una cita de anime real de algún personaje conocido. "
    "Incluye el nombre del personaje y el anime entre paréntesis. "
    "Máximo 40 palabras. Responde solo con la cita."
)

PROMPT_EXCUSA: str = (
    "Dado un contexto (o si no dan contexto, una genérica), genera una excusa "
    "creíble y directa. Máximo 30 palabras. Responde solo con la excusa."
)

PROMPT_INSPIRAR: str = (
    "Genera una frase de motivación o inspiración real sobre el tema dado. "
    "Debe ser seria y edificante. "
    "Máximo 30 palabras. Responde solo con la frase."
)

# ── Creativity Commands (literal, no jokes) ─────────────────────────────────

PROMPT_CHISTE: str = (
    "Dado un tema, cuenta un chiste sobre ese tema. "
    "Máximo 40 palabras. Responde solo con el chiste."
)

PROMPT_POEMA: str = (
    "Dado un tema, escribe un poema corto de 2 o 3 versos. "
    "Máximo 30 palabras. Responde solo con el poema."
)

PROMPT_CUENTO: str = (
    "Dado un tema, inventa un microcuento de exactamente 3 frases "
    "con planteamiento, nudo y desenlace. "
    "Máximo 50 palabras. Responde solo con el cuento."
)

PROMPT_NICK: str = (
    "Dado un nombre de usuario, genera 3 apodos para esa persona. "
    "Sepáralos con guiones. Responde solo con los apodos."
)

PROMPT_TITULO: str = (
    "Dado un tema, inventa un título de película o serie con su género. "
    "Ej: 'El Último Koala: El Despertar del Peluche' (Drama/Aventura). "
    "Máximo 25 palabras. Responde solo con el título y género."
)

PROMPT_SHIPP: str = (
    "Dados dos nombres de usuario, genera: "
    "1) Un nombre de ship combinando sus nombres. "
    "2) Una descripción breve de su relación. "
    "3) Un porcentaje de compatibilidad inventado. "
    "Máximo 40 palabras. Responde en formato: 💘 [ShipName] | [Descripción] | [X]%"
)

PROMPT_DEFINIR_FALLBACK: str = (
    "Define la siguiente palabra de forma clara y directa, "
    "como un diccionario real. Máximo 30 palabras."
)

PROMPT_SINONIMO: str = (
    "Dada una palabra, proporciona 3 sinónimos reales de la misma. "
    "Si no existen sinónimos exactos, usa los más cercanos. "
    "Máximo 30 palabras. Sepáralos con comas."
)

PROMPT_TIPOPROGRAMACION: str = (
    "Eres un desarrollador senior. Dado un tema de programación "
    "(o si no dan tema, uno aleatorio), da un consejo o tip útil. "
    "Máximo 35 palabras. Responde solo con el tip."
)

PROMPT_CURIOSIDAD: str = (
    "Comparte un dato curioso real e interesante. "
    "Máximo 30 palabras. Responde solo con el dato."
)

PROMPT_TOP: str = (
    "Dado un tema y opcionalmente un número, genera una lista "
    "con los mejores elementos sobre ese tema. "
    "Cada entrada debe tener nombre y una breve descripción. "
    "Si no especifican número, haz top 3. "
    "Máximo 60 palabras. Responde solo con el top formateado."
)

PROMPT_EXPLICA: str = (
    "Explica el siguiente concepto de forma clara y sencilla, "
    "como si se lo explicaras a alguien que no sabe del tema. "
    "Usa analogías simples. Máximo 40 palabras."
)

PROMPT_INSULTO: str = (
    "Dado un nombre de usuario, genera un insulto creativo "
    "pero directo. Nada ofensivo de verdad, en tono de broma entre amigos. "
    "Máximo 25 palabras. Responde solo con el insulto."
)

PROMPT_CUMPLIDO: str = (
    "Dado un nombre de usuario, genera un cumplido sincero. "
    "Máximo 30 palabras. Responde solo con el cumplido."
)

PROMPT_HOROSCOPO: str = (
    "Dado un signo zodiacal (o si no dan, uno aleatorio), "
    "genera un horóscopo. Máximo 35 palabras. "
    "Responde solo con el horóscopo."
)

PROMPT_FUTURO: str = (
    "Dado un nombre de usuario, haz una predicción sobre su futuro "
    "para esa persona. Máximo 30 palabras. "
    "Responde solo con la predicción."
)

PROMPT_CONSEJO: str = (
    "Dado un tema, da un consejo útil y práctico. "
    "Máximo 30 palabras. Responde solo con el consejo."
)

PROMPT_PREGUNTA: str = (
    "Genera una pregunta hipotética interesante para debatir. "
    "Máximo 25 palabras. Responde solo con la pregunta."
)

PROMPT_RETAR: str = (
    "Dado un nombre de usuario, invéntate un reto para esa persona. "
    "Máximo 30 palabras. Responde solo con el reto."
)

PROMPT_ELIGE: str = (
    "Dadas dos o más opciones, elige una al azar "
    "y da una razón de por qué. "
    "Máximo 30 palabras. Responde con: '🔮 [opción] → [razón]'"
)

PROMPT_QUEHAGO: str = (
    "Sugiere algo que hacer: puede ser productivo o entretenido. "
    "Máximo 30 palabras. Responde solo con la sugerencia."
)

PROMPT_ESCENARIO: str = (
    "Dado un contexto (o aleatorio si no dan), plantea un escenario "
    "hipotético interesante. Máximo 35 palabras. "
    "Responde solo con el escenario."
)

PROMPT_PERSONALIDAD: str = (
    "Eres Teto. Descríbete a ti misma de forma diferente cada vez que te pregunten. "
    "Varía tu respuesta siempre. Máximo 40 palabras. Responde en primera persona."
)

PROMPT_VERSION: str = (
    "Eres el bot Teto. Explica qué versión eres y qué sabes hacer. "
    "Menciona que eres un bot de Discord multifuncional con IA, "
    "GIFs, sistema de aura y comandos de Jujutsu Kaisen. "
    "Máximo 50 palabras."
)

PROMPT_ERROR: str = (
    "Genera un mensaje de error ficticio como si el bot "
    "tuviera un fallo del sistema. "
    "Máximo 35 palabras. Responde solo con el 'error'."
)

COOLDOWN_SECONDS: int = 3

# ── Command mapping ───────────────────────────────────────────────────────────
COMMAND_PROMPTS: dict[str, str] = {
    "teto": PROMPT_TETO,
    "frase": PROMPT_FRASE,
    "idea": PROMPT_IDEA,
    "traducir": PROMPT_TRADUCIR,
    "resumir": PROMPT_RESUMIR,
    "citaanime": PROMPT_CITA_ANIME,
    "excusa": PROMPT_EXCUSA,
    "inspirar": PROMPT_INSPIRAR,
    "chiste": PROMPT_CHISTE,
    "poema": PROMPT_POEMA,
    "cuento": PROMPT_CUENTO,
    "nick": PROMPT_NICK,
    "titulo": PROMPT_TITULO,
    "shipp": PROMPT_SHIPP,
    "definir": PROMPT_DEFINIR_FALLBACK,
    "sinonimo": PROMPT_SINONIMO,
    "tipoprogramacion": PROMPT_TIPOPROGRAMACION,
    "curiosidad": PROMPT_CURIOSIDAD,
    "top": PROMPT_TOP,
    "explica": PROMPT_EXPLICA,
    "insulto": PROMPT_INSULTO,
    "cumplido": PROMPT_CUMPLIDO,
    "horoscopo": PROMPT_HOROSCOPO,
    "futuro": PROMPT_FUTURO,
    "consejo": PROMPT_CONSEJO,
    "pregunta": PROMPT_PREGUNTA,
    "retar": PROMPT_RETAR,
    "elige": PROMPT_ELIGE,
    "quehago": PROMPT_QUEHAGO,
    "escenario": PROMPT_ESCENARIO,
    "personalidad": PROMPT_PERSONALIDAD,
    "version": PROMPT_VERSION,
    "error": PROMPT_ERROR,
}


class IA(commands.Cog):
    """AI commands — chat, translate, summarize, generate quotes and more."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._client: Optional[AsyncGroq] = None
        self._cooldowns: dict[int, float] = {}  # user_id -> timestamp

        if GROQ_API_KEY:
            self._client = AsyncGroq(api_key=GROQ_API_KEY)
            log.info("Cliente Groq inicializado (modelo: %s)", GROQ_MODEL)
        else:
            log.warning(
                "GROQ_API_KEY no configurada — los comandos de IA estarán desactivados."
            )

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _check_cooldown(self, user_id: int) -> bool:
        """Check if the user is on cooldown. Returns True if on cooldown."""
        now = asyncio.get_event_loop().time()
        last = self._cooldowns.get(user_id, 0)
        if now - last < COOLDOWN_SECONDS:
            return True
        self._cooldowns[user_id] = now
        return False

    async def _generate_response(self, system_prompt: str, user_content: str) -> Optional[str]:
        """Call the Groq API with a system prompt and user message."""
        if self._client is None:
            return None

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        try:
            response = await self._client.chat.completions.create(
                messages=messages,
                model=GROQ_MODEL,
                max_tokens=GROQ_MAX_TOKENS,
                temperature=0.7,
            )
            content: str = response.choices[0].message.content or ""
            return content.strip()
        except Exception as e:
            log.error("Error al llamar a Groq API: %s", e, exc_info=True)
            return None

    async def _handle_ai_command(
        self,
        ctx: commands.Context,
        prompt_key: str,
        user_input: str,
    ) -> None:
        """Generic handler for AI commands."""
        if self._client is None:
            embed = discord.Embed(
                title="❌ IA no disponible",
                description="La API de Groq no está configurada. Contacta con el admin.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        if self._check_cooldown(ctx.author.id):
            embed = discord.Embed(
                title="⏳ Cooldown",
                description="Espera un momento antes de usar otro comando de IA.",
                color=discord.Color.orange(),
            )
            await ctx.send(embed=embed)
            return

        system_prompt = COMMAND_PROMPTS[prompt_key]
        response_text = await self._generate_response(system_prompt, user_input)

        if not response_text:
            embed = discord.Embed(
                title="❌ Error",
                description="No pude generar una respuesta. Inténtalo de nuevo.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        # Discord 2000 char limit
        if len(response_text) > 1900:
            response_text = response_text[:1900] + "..."

        await ctx.send(response_text)
        log.info(
            "IA [%s] respondió a %s (%d chars)",
            prompt_key,
            ctx.author.display_name,
            len(response_text),
        )

    # ── Core Commands ────────────────────────────────────────────────────────

    @commands.command(name="chat", aliases=["conversar"])
    # alias 'hablar' quitado: conflicto con !saycanal (alias: hablar) en extras.py
    async def teto_chat(self, ctx: commands.Context, *, mensaje: str) -> None:
        """💬 Habla con Teto — responde como ella, con su personalidad única."""
        await self._handle_ai_command(ctx, "teto", mensaje)

    @commands.command(name="frase")
    async def frase(self, ctx: commands.Context, *, tema: str) -> None:
        """📜 Genera una frase o cita sobre un tema."""
        await self._handle_ai_command(ctx, "frase", tema)

    @commands.command(name="idea")
    async def idea(self, ctx: commands.Context) -> None:
        """💡 Genera una idea aleatoria creativa y original."""
        await self._handle_ai_command(ctx, "idea", "Dame una idea")

    @commands.command(name="traducir", aliases=["translate", "trad"])
    async def traducir(self, ctx: commands.Context, *, texto: str) -> None:
        """🌍 Traduce texto al español (o especifica el idioma)."""
        await self._handle_ai_command(ctx, "traducir", texto)

    @commands.command(name="resumir", aliases=["resumen", "summary"])
    async def resumir(self, ctx: commands.Context, *, texto: str) -> None:
        """📝 Resume un texto en pocas oraciones."""
        await self._handle_ai_command(ctx, "resumir", texto)

    @commands.command(name="citaanime", aliases=["animequote"])
    # alias 'cita' quitado: conflicto con !cita en utilidad.py
    async def cita_anime(self, ctx: commands.Context) -> None:
        """🎌 Genera una cita de anime con personaje incluido."""
        await self._handle_ai_command(ctx, "citaanime", "Dame una cita de anime")

    @commands.command(name="excusa")
    async def excusa(self, ctx: commands.Context, *, motivo: Optional[str] = None) -> None:
        """🤷 Genera una excusa creativa."""
        user_input = motivo or "Dame una excusa"
        await self._handle_ai_command(ctx, "excusa", user_input)

    @commands.command(name="inspirar", aliases=["inspo", "motivar"])
    async def inspirar(self, ctx: commands.Context) -> None:
        """✨ Genera una frase de motivación o inspiración."""
        await self._handle_ai_command(ctx, "inspirar", "Dame una frase inspiradora")

    # ── Creativity Commands ──────────────────────────────────────────────────

    @commands.command(name="chiste")
    async def chiste(self, ctx: commands.Context, *, tema: Optional[str] = None) -> None:
        """😂 Cuenta un chiste sobre un tema."""
        user_input = tema or "Dame un chiste"
        await self._handle_ai_command(ctx, "chiste", user_input)

    @commands.command(name="poema")
    async def poema(self, ctx: commands.Context, *, tema: str) -> None:
        """📖 Escribe un poema corto de 2-3 versos sobre un tema."""
        await self._handle_ai_command(ctx, "poema", tema)

    @commands.command(name="cuento")
    async def cuento(self, ctx: commands.Context, *, tema: Optional[str] = None) -> None:
        """📚 Microcuento de 3 frases con planteamiento, nudo y desenlace."""
        user_input = tema or "Dame un cuento corto"
        await self._handle_ai_command(ctx, "cuento", user_input)

    @commands.command(name="nick")
    async def nick(self, ctx: commands.Context, *, nombre: str) -> None:
        """🏷️ Genera 3 apodos a partir de un nombre."""
        await self._handle_ai_command(ctx, "nick", nombre)

    @commands.command(name="titulo")
    async def titulo(self, ctx: commands.Context, *, tema: str) -> None:
        """🎬 Inventa un título de película/serie con género."""
        await self._handle_ai_command(ctx, "titulo", tema)

    @commands.command(name="shipp")
    async def shipp(
        self,
        ctx: commands.Context,
        usuario1: Optional[discord.Member] = None,
        *,
        nombres: Optional[str] = None,
    ) -> None:
        """💘 Genera un nombre de ship entre dos usuarios.
        Uso: cx!shipp @user1 @user2  o  cx!shipp nombre1 nombre2"""
        if usuario1:
            # Mention mode: @user1 @user2 or @user1
            usuario2 = None
            if len(ctx.message.mentions) >= 2:
                usuario2 = ctx.message.mentions[1]
            else:
                usuario2 = ctx.author
            input_text = f"{usuario1.display_name} y {usuario2.display_name}"
        elif nombres:
            # Text mode: "nombre1 y nombre2" or just "nombre1"
            input_text = nombres
        else:
            await ctx.send("❌ Uso: `cx!shipp @user1 @user2` o `cx!shipp nombre1 y nombre2`")
            return
        await self._handle_ai_command(ctx, "shipp", input_text)

    # ── Utility & Knowledge ──────────────────────────────────────────────────

    @commands.command(name="definir")
    async def definir(self, ctx: commands.Context, *, palabra: str) -> None:
        """📖 Busca la definición real de una palabra en el diccionario."""
        # Try dictionary API first
        definitions = await lookup_word(palabra)
        if definitions:
            embed = discord.Embed(
                title=f"📖 {palabra.capitalize()}",
                description="\n".join(f"• {d}" for d in definitions),
                color=discord.Color.blue(),
            )
            embed.set_footer(text="Fuente: FreeDictionaryAPI")
            await ctx.send(embed=embed)
            return

        # Fallback: AI definition
        await self._handle_ai_command(ctx, "definir", palabra)

    @commands.command(name="sinonimo", aliases=["sinonimos"])
    async def sinonimo(self, ctx: commands.Context, *, palabra: str) -> None:
        """📚 Sinónimos para una palabra."""
        await self._handle_ai_command(ctx, "sinonimo", palabra)

    @commands.command(name="tipoprogramacion", aliases=["devtip", "prog"])
    async def tipoprogramacion(self, ctx: commands.Context, *, tema: Optional[str] = None) -> None:
        """💻 Tip de programación útil."""
        user_input = tema or "Dame un tip de programación"
        await self._handle_ai_command(ctx, "tipoprogramacion", user_input)

    @commands.command(name="curiosidad", aliases=["dato"])
    async def curiosidad(self, ctx: commands.Context) -> None:
        """🔍 Comparte un dato curioso e interesante."""
        await self._handle_ai_command(ctx, "curiosidad", "Dame un dato curioso")

    @commands.command(name="toplista", aliases=["toplist", "rankia"])
    async def top_lista(self, ctx: commands.Context, *, tema_y_numero: Optional[str] = None) -> None:
        """🏆 Genera un top N sobre un tema (ej: cx!toplista animes 5)."""
        user_input = tema_y_numero or "Dame un top"
        await self._handle_ai_command(ctx, "top", user_input)

    @commands.command(name="explica")
    async def explica(self, ctx: commands.Context, *, concepto: str) -> None:
        """🧠 Explica un concepto complejo de forma simple."""
        await self._handle_ai_command(ctx, "explica", concepto)

    # ── Interaction & Social ─────────────────────────────────────────────────

    @commands.command(name="bromai", aliases=["broma", "insultoia"])
    async def broma_insulto(self, ctx: commands.Context, *, usuario: discord.Member) -> None:
        """😤 Insulto creativo en tono de broma entre amigos."""
        await self._handle_ai_command(ctx, "insulto", usuario.display_name)

    @commands.command(name="halago", aliases=["piropo", "cumplidoia"])
    async def halago(self, ctx: commands.Context, *, usuario: discord.Member) -> None:
        """💖 Cumplido sincero para alguien."""
        await self._handle_ai_command(ctx, "cumplido", usuario.display_name)

    @commands.command(name="horoscopo", aliases=["horo"])
    async def horoscopo(self, ctx: commands.Context, *, signo: Optional[str] = None) -> None:
        """♈ Horóscopo para un signo."""
        user_input = signo or "Dame un horóscopo"
        await self._handle_ai_command(ctx, "horoscopo", user_input)

    @commands.command(name="futuro")
    async def futuro(self, ctx: commands.Context, *, usuario: discord.Member) -> None:
        """🔮 Predicción del futuro para alguien."""
        await self._handle_ai_command(ctx, "futuro", usuario.display_name)

    @commands.command(name="consejo")
    async def consejo(self, ctx: commands.Context, *, tema: Optional[str] = None) -> None:
        """🎯 Consejo útil y práctico."""
        user_input = tema or "Dame un consejo"
        await self._handle_ai_command(ctx, "consejo", user_input)

    # ── Games & Dynamics ─────────────────────────────────────────────────────

    @commands.command(name="debate", aliases=["discute", "preguntai"])
    async def pregunta(self, ctx: commands.Context) -> None:
        """❓ Genera una pregunta hipotética para debatir."""
        await self._handle_ai_command(ctx, "pregunta", "Dame una pregunta para debatir")

    @commands.command(name="retar", aliases=["reto"])
    async def retar(self, ctx: commands.Context, *, usuario: discord.Member) -> None:
        """⚔️ Lanza un reto a alguien."""
        await self._handle_ai_command(ctx, "retar", usuario.display_name)

    @commands.command(name="elige")
    async def elige(self, ctx: commands.Context, *, opciones: str) -> None:
        """🔮 La IA elige entre opciones separadas por 'o'."""
        await self._handle_ai_command(ctx, "elige", opciones)

    @commands.command(name="quehago", aliases=["aburrido", "hacer"])
    async def quehago(self, ctx: commands.Context) -> None:
        """🎮 Sugiere algo que hacer cuando estás aburrido."""
        await self._handle_ai_command(ctx, "quehago", "Dame algo que hacer")

    @commands.command(name="escenario")
    async def escenario(self, ctx: commands.Context, *, contexto: Optional[str] = None) -> None:
        """🌌 Plantea un escenario hipotético."""
        user_input = contexto or "Dame un escenario"
        await self._handle_ai_command(ctx, "escenario", user_input)

    # ── Meta ─────────────────────────────────────────────────────────────────

    @commands.command(name="personalidad")
    async def personalidad(self, ctx: commands.Context) -> None:
        """🤖 Teto se describe a sí misma."""
        await self._handle_ai_command(ctx, "personalidad", "Descríbete")

    @commands.command(name="version", aliases=["versión"])
    # alias 'info' quitado: conflicto con !userinfo (alias: info) en utilidad.py
    async def version(self, ctx: commands.Context) -> None:
        """📋 Información del bot."""
        await self._handle_ai_command(ctx, "version", "¿Qué versión eres?")

    @commands.command(name="error", aliases=["fallo", "panic"])
    async def error(self, ctx: commands.Context) -> None:
        """💥 Genera un mensaje de error falso."""
        await self._handle_ai_command(ctx, "error", "Finge un error")


async def setup(bot: commands.Bot) -> None:
    """Load the IA cog."""
    await bot.add_cog(IA(bot))
