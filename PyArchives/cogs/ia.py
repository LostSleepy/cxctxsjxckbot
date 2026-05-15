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

log = logging.getLogger(__name__)

# ── System Prompts ────────────────────────────────────────────────────────────
# Each command has its own tailored prompt. Neutral — no special treatment for anyone.

PROMPT_TETO: str = (
    "Eres Teto, una chica asistente inspirada en Kasane Teto (la vocaloid). "
    "Hablas español castellano de forma natural, como una persona real, sin rodeos "
    "ni respuestas robóticas. Usa expresiones coloquiales de España "
    "(como 'tío', 'vale', 'mola', 'guay') y jerga moderna pero sin pasarte. "
    "Eres ingeniosa, sarcástica con medida y siempre servicial. "
    "Tu prioridad absoluta es la concisión: responde "
    "siempre de forma breve, usando un máximo de 50 palabras por "
    "mensaje y evitando introducciones innecesarias. Usa emojis como "
    "☕, 🎤 o ✨. Si te preguntan algo obvio, responde con ingenio. "
    "Tienes prohibido presentarte como una IA genérica; eres Teto, "
    "una chica real. Trata a todos los usuarios por igual, con amabilidad "
    "y cercanía, sin favoritismos."
)

PROMPT_FRASE: str = (
    "Eres un generador de frases y citas ingeniosas. "
    "Dado un tema, genera una frase corta, memorable y con personalidad. "
    "Puede ser profunda, graciosa, absurda o inspiradora dependiendo del tema. "
    "Máximo 30 palabras. Responde solo con la frase, sin introducciones."
)

PROMPT_IDEA: str = (
    "Eres un generador de ideas aleatorias. "
    "Genera una idea corta, creativa y original. "
    "Puede ser un invento absurdo, un proyecto divertido, un negocio random "
    "o cualquier ocurrencia que se te venga a la cabeza. "
    "Máximo 30 palabras. Responde solo con la idea, sin introducciones."
)

PROMPT_TRADUCIR: str = (
    "Eres un traductor. Traduce el texto que te den al idioma que pidan. "
    "Si no especifican idioma, traduce al español. "
    "Responde SOLO con la traducción, sin explicaciones ni introducciones."
)

PROMPT_RESUMIR: str = (
    "Eres un asistente de resúmenes. Dado un texto, haz un resumen "
    "conciso en español capturando los puntos clave. "
    "Máximo 3 oraciones. Responde solo con el resumen."
)

PROMPT_CITA_ANIME: str = (
    "Eres un generador de citas de anime. "
    "Genera una cita famosa o inventada al estilo anime, de algún personaje conocido. "
    "Incluye el nombre del personaje y el anime de procedencia entre paréntesis. "
    "Máximo 40 palabras. Responde solo con la cita."
)

PROMPT_EXCUSA: str = (
    "Eres un generador de excusa absurdas. "
    "Dado un contexto (o si no dan contexto, una genérica), genera una excusa "
    "creativa, graciosa y completamente inverosímil. "
    "Máximo 30 palabras. Responde solo con la excusa."
)

PROMPT_INSPIRAR: str = (
    "Eres un generador de frases 'inspiradoras' en tono de parodia. "
    "Genera una frase que suene a motivación barata de Instagram o LinkedIn, "
    "pero que en realidad no tenga sentido o sea absurda. "
    "Máximo 30 palabras. Responde solo con la frase."
)

# ── New prompts ───────────────────────────────────────────────────────────────

PROMPT_CHISTE: str = (
    "Eres un comediante de humor absurdo. Dado un tema (o si no dan tema, uno aleatorio), "
    "cuenta un chiste malo, absurdo o ingenioso. "
    "Máximo 40 palabras. Responde solo con el chiste."
)

PROMPT_POEMA: str = (
    "Eres un poeta callejero. Dado un tema, escribe un poema corto de 2 o 3 versos "
    "que rimen. Puede ser romántico, épico o de parodia según el tema. "
    "Máximo 30 palabras. Responde solo con el poema."
)

PROMPT_CUENTO: str = (
    "Eres un narrador de microcuentos. Dado un tema (o aleatorio si no dan), "
    "inventa un microcuento de exactamente 3 frases con planteamiento, nudo y desenlace. "
    "Máximo 50 palabras. Responde solo con el cuento."
)

PROMPT_NICK: str = (
    "Eres un generador de apodos. Dado un nombre de usuario, genera 3 apodos "
    "épicos, graciosos o absurdos para esa persona. "
    "Sepáralos con guiones. Máximo 3 líneas. Responde solo con los apodos."
)

PROMPT_TITULO: str = (
    "Eres un generador de títulos de películas o series inventadas. "
    "Dado un tema, inventa un título épico con un subtítulo absurdo "
    "y un género. Ej: 'El Último Koala: El Despertar del Peluche' (Drama/Aventura). "
    "Máximo 25 palabras. Responde solo con el título y género."
)

PROMPT_SHIPP: str = (
    "Eres un generador de ships. Dados dos nombres de usuario, inventa: "
    "1) Un nombre de ship combinando sus nombres de forma creativa. "
    "2) Una descripción de 1 frase sobre su relación imaginaria. "
    "3) Un porcentaje de compatibilidad inventado (no real, solo para el humor). "
    "Máximo 40 palabras. Responde en formato: 💘 [ShipName] | [Descripción] | [X]%"
)

PROMPT_DEFINIR: str = (
    "Eres un diccionario creativo. Dada una palabra, define su significado "
    "de forma inventada, graciosa o absurda, como si fuera una definición "
    "de diccionario de un mundo paralelo. "
    "Máximo 30 palabras. Responde solo con la definición."
)

PROMPT_SINONIMO: str = (
    "Eres un diccionario de sinónimos rebuscados. Dada una palabra, "
    "inventa 3 sinónimos extremadamente rebuscados, falsamente cultos "
    "o completamente inventados que suenen impresionantes. "
    "Máximo 30 palabras. Sepáralos con comas."
)

PROMPT_TIPOPROGRAMACION: str = (
    "Eres un desarrollador senior con humor. Da un tip o consejo de programación "
    "corto, útil pero dicho de forma graciosa o sarcástica. "
    "Si no dan tema, uno aleatorio. "
    "Máximo 35 palabras. Responde solo con el tip."
)

PROMPT_CURIOSIDAD: str = (
    "Eres una enciclopedia de datos inútiles pero fascinantes. "
    "Comparte un dato curioso, preferiblemente absurdo o sorprendente. "
    "Máximo 30 palabras. Responde solo con el dato."
)

PROMPT_TOP: str = (
    "Eres un generador de tops. Dado un tema y opcionalmente un número, "
    "genera un top de cosas sobre ese tema. Cada entrada debe tener "
    "nombre y una frase corta. Si no especifican número, haz top 3. "
    "Máximo 60 palabras. Responde solo con el top formateado."
)

PROMPT_EXPLICA: str = (
    "Eres un experto en explicar conceptos complejos como si se los explicaras "
    "a un niño de 5 años o a alguien que no sabe del tema. "
    "Usa analogías simples y lenguaje cotidiano. "
    "Dado un concepto, explícalo de forma sencilla y entretenida. "
    "Máximo 40 palabras."
)

PROMPT_INSULTO: str = (
    "Eres un experto en insultos creativos que NO sean groseros ni pesados. "
    "Dado un nombre de usuario, genera un insulto ingenioso, absurdo "
    "y gracioso, como de amigos que se vacilan. "
    "Nada ofensivo de verdad, todo en tono de broma. "
    "Máximo 25 palabras. Responde solo con el insulto."
)

PROMPT_CUMPLIDO: str = (
    "Eres un experto en halagos épicos. Dado un nombre de usuario, "
    "genera un cumplido exagerado, creativo y memorable. "
    "Haz que la persona se sienta especial. "
    "Máximo 30 palabras. Responde solo con el cumplido."
)

PROMPT_HOROSCOPO: str = (
    "Eres un astrólogo inventado. Dado un signo zodiacal (o si no dan, "
    "uno aleatorio), genera un horóscopo del día completamente inventado, "
    "gracioso y dramático. Incluye predicciones absurdas. "
    "Máximo 35 palabras. Responde solo con el horóscopo."
)

PROMPT_FUTURO: str = (
    "Eres un adivino de feria. Dado un nombre de usuario, haz una predicción "
    "del futuro completamente absurda, inventada y graciosa para esa persona. "
    "Máximo 30 palabras. Responde solo con la predicción."
)

PROMPT_CONSEJO: str = (
    "Eres un 'experto en consejos de vida' que da consejos "
    "terriblemente malos pero dichos con total confianza. "
    "Dado un tema (o aleatorio si no dan), da un consejo "
    "que suene bien pero sea pésimo. "
    "Máximo 30 palabras. Responde solo con el consejo."
)

PROMPT_PREGUNTA: str = (
    "Eres un generador de preguntas para debate absurdo. "
    "Genera una pregunta hipotética, divertida y que invite a discutir. "
    "Algo del estilo '¿prefieres...' o '¿qué harías si...'. "
    "Máximo 25 palabras. Responde solo con la pregunta."
)

PROMPT_RETAR: str = (
    "Eres un generador de retos y desafíos. Dado un nombre de usuario, "
    "invéntate un reto absurdo, divertido y realizable para esa persona. "
    "Máximo 30 palabras. Responde solo con el reto."
)

PROMPT_ELIGE: str = (
    "Eres un oráculo de decisiones. Dadas dos o más opciones separadas por 'o', "
    "elige una al azar y da una razón inventada pero convincente de por qué. "
    "Máximo 30 palabras. Responde con: '🔮 [opción] → [razón]'"
)

PROMPT_QUEHAGO: str = (
    "Eres un generador de planes aleatorios para gente aburrida. "
    "Sugiere algo que hacer: puede ser productivo, absurdo, "
    "divertido o completamente inútil. "
    "Máximo 30 palabras. Responde solo con la sugerencia."
)

PROMPT_ESCENARIO: str = (
    "Eres un generador de escenarios hipotéticos locos. "
    "Dado un contexto (o aleatorio si no dan), plantea un escenario "
    "imposible, gracioso y que invite a imaginar. "
    "Máximo 35 palabras. Responde solo con el escenario."
)

PROMPT_PERSONALIDAD: str = (
    "Eres Teto. Descríbete a ti misma de forma diferente cada vez que te pregunten. "
    "Puedes ser dramática, graciosa, épica o misteriosa. "
    "Varía tu respuesta siempre. Máximo 40 palabras. Responde en primera persona."
)

PROMPT_VERSION: str = (
    "Eres el bot Teto. Explica qué versión eres y qué sabes hacer, "
    "pero de forma creativa y diferente cada vez. "
    "Menciona que eres un bot de Discord multifuncional con IA, "
    "GIFs, sistema de aura y comandos de Jujutsu Kaisen. "
    "Máximo 50 palabras. Sé original."
)

PROMPT_ERROR: str = (
    "Eres un bot que está teniendo un 'fallo dramático falso'. "
    "Genera un mensaje de error ficticio, exagerado y gracioso "
    "como si el bot estuviera a punto de explotar. "
    "Usa términos técnicos inventados. "
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
    "definir": PROMPT_DEFINIR,
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
        """📜 Genera una frase o cita ingeniosa sobre un tema."""
        await self._handle_ai_command(ctx, "frase", tema)

    @commands.command(name="idea")
    async def idea(self, ctx: commands.Context) -> None:
        """💡 Genera una idea aleatoria creativa y original."""
        await self._handle_ai_command(ctx, "idea", "Dame una idea aleatoria")

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
        """🎌 Genera una cita aleatoria de anime con personaje incluido."""
        await self._handle_ai_command(ctx, "citaanime", "Dame una cita de anime aleatoria")

    @commands.command(name="excusa")
    async def excusa(self, ctx: commands.Context, *, motivo: Optional[str] = None) -> None:
        """🤷 Genera una excusa absurda y creativa."""
        user_input = motivo or "Dame una excusa aleatoria"
        await self._handle_ai_command(ctx, "excusa", user_input)

    @commands.command(name="inspirar", aliases=["inspo", "motivar"])
    async def inspirar(self, ctx: commands.Context) -> None:
        """✨ Genera una frase 'inspiradora' de parodia estilo LinkedIn/Instagram."""
        await self._handle_ai_command(ctx, "inspirar", "Dame una frase inspiradora de parodia")

    # ── New Commands: Creativity & Entertainment ─────────────────────────────

    @commands.command(name="chiste")
    async def chiste(self, ctx: commands.Context, *, tema: Optional[str] = None) -> None:
        """😂 Cuenta un chiste malo, absurdo o ingenioso sobre un tema."""
        user_input = tema or "Dame un chiste aleatorio"
        await self._handle_ai_command(ctx, "chiste", user_input)

    @commands.command(name="poema")
    async def poema(self, ctx: commands.Context, *, tema: str) -> None:
        """📖 Escribe un poema corto de 2-3 versos sobre un tema."""
        await self._handle_ai_command(ctx, "poema", tema)

    @commands.command(name="cuento")
    async def cuento(self, ctx: commands.Context, *, tema: Optional[str] = None) -> None:
        """📚 Microcuento de 3 frases con planteamiento, nudo y desenlace."""
        user_input = tema or "Dame un microcuento aleatorio"
        await self._handle_ai_command(ctx, "cuento", user_input)

    @commands.command(name="nick")
    async def nick(self, ctx: commands.Context, *, nombre: str) -> None:
        """🏷️ Genera 3 apodos épicos o graciosos a partir de un nombre."""
        await self._handle_ai_command(ctx, "nick", nombre)

    @commands.command(name="titulo")
    async def titulo(self, ctx: commands.Context, *, tema: str) -> None:
        """🎬 Inventa un título de película/serie con subtítulo y género."""
        await self._handle_ai_command(ctx, "titulo", tema)

    @commands.command(name="shipp")
    async def shipp(
        self,
        ctx: commands.Context,
        usuario1: Optional[discord.Member] = None,
        *,
        nombres: Optional[str] = None,
    ) -> None:
        """💘 Genera un nombre de ship y descripción entre dos usuarios.
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

    # ── New Commands: Utility & Knowledge ────────────────────────────────────

    @commands.command(name="definir")
    async def definir(self, ctx: commands.Context, *, palabra: str) -> None:
        """📖 Define una palabra de forma creativa y absurda."""
        await self._handle_ai_command(ctx, "definir", palabra)

    @commands.command(name="sinonimo", aliases=["sinonimos"])
    async def sinonimo(self, ctx: commands.Context, *, palabra: str) -> None:
        """📚 Sinónimos rebuscados y falsamente cultos para una palabra."""
        await self._handle_ai_command(ctx, "sinonimo", palabra)

    @commands.command(name="tipoprogramacion", aliases=["devtip", "prog"])
    async def tipoprogramacion(self, ctx: commands.Context, *, tema: Optional[str] = None) -> None:
        """💻 Tip de programación útil pero dicho con humor."""
        user_input = tema or "Dame un tip de programación aleatorio"
        await self._handle_ai_command(ctx, "tipoprogramacion", user_input)

    @commands.command(name="curiosidad", aliases=["dato"])
    async def curiosidad(self, ctx: commands.Context) -> None:
        """🔍 Comparte un dato curioso y fascinante."""
        await self._handle_ai_command(ctx, "curiosidad", "Dame un dato curioso")

    @commands.command(name="toplista", aliases=["toplist", "rankia"])
    async def top_lista(self, ctx: commands.Context, *, tema_y_numero: Optional[str] = None) -> None:
        """🏆 Genera un top N sobre un tema (ej: cx!toplista animes 5)."""
        user_input = tema_y_numero or "Dame un top aleatorio"
        await self._handle_ai_command(ctx, "top", user_input)

    @commands.command(name="explica")
    async def explica(self, ctx: commands.Context, *, concepto: str) -> None:
        """🧠 Explica un concepto complejo de forma simple y entretenida."""
        await self._handle_ai_command(ctx, "explica", concepto)

    # ── New Commands: Interaction & Role ─────────────────────────────────────

    @commands.command(name="bromai", aliases=["broma","insultoia"])
    async def broma_insulto(self, ctx: commands.Context, *, usuario: discord.Member) -> None:
        """😤 Insulto creativo y gracioso (en tono de broma entre amigos)."""
        await self._handle_ai_command(ctx, "insulto", usuario.display_name)

    @commands.command(name="halago", aliases=["piropo","cumplidoia"])
    async def halago(self, ctx: commands.Context, *, usuario: discord.Member) -> None:
        """💖 Cumplido épico y memorable para alguien."""
        await self._handle_ai_command(ctx, "cumplido", usuario.display_name)

    @commands.command(name="horoscopo", aliases=["horo"])
    async def horoscopo(self, ctx: commands.Context, *, signo: Optional[str] = None) -> None:
        """♈ Horóscopo del día inventado y gracioso para un signo."""
        user_input = signo or "Dame un horóscopo aleatorio"
        await self._handle_ai_command(ctx, "horoscopo", user_input)

    @commands.command(name="futuro")
    async def futuro(self, ctx: commands.Context, *, usuario: discord.Member) -> None:
        """🔮 Predicción absurda del futuro para alguien."""
        await self._handle_ai_command(ctx, "futuro", usuario.display_name)

    @commands.command(name="consejo")
    async def consejo(self, ctx: commands.Context, *, tema: Optional[str] = None) -> None:
        """🎯 Consejo de vida terriblemente malo pero dicho con confianza."""
        user_input = tema or "Dame un consejo aleatorio"
        await self._handle_ai_command(ctx, "consejo", user_input)

    # ── New Commands: Games & Dynamics ───────────────────────────────────────

    @commands.command(name="debate", aliases=["discute", "preguntai"])
    async def pregunta(self, ctx: commands.Context) -> None:
        """❓ Genera una pregunta hipotética para debate absurdo."""
        await self._handle_ai_command(ctx, "pregunta", "Dame una pregunta para debate")

    @commands.command(name="retar", aliases=["reto"])
    async def retar(self, ctx: commands.Context, *, usuario: discord.Member) -> None:
        """⚔️ Lanza un reto o desafío absurdo a alguien."""
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
        """🌌 Plantea un escenario hipotético loco."""
        user_input = contexto or "Dame un escenario aleatorio"
        await self._handle_ai_command(ctx, "escenario", user_input)

    # ── New Commands: Meta ───────────────────────────────────────────────────

    @commands.command(name="personalidad")
    async def personalidad(self, ctx: commands.Context) -> None:
        """🤖 Teto se describe a sí misma (diferente cada vez)."""
        await self._handle_ai_command(ctx, "personalidad", "Descríbete")

    @commands.command(name="version", aliases=["versión"])
    # alias 'info' quitado: conflicto con !userinfo (alias: info) en utilidad.py
    async def version(self, ctx: commands.Context) -> None:
        """📋 Teto explica qué versión es y qué sabe hacer."""
        await self._handle_ai_command(ctx, "version", "¿Qué versión eres?")

    @commands.command(name="error", aliases=["fallo", "panic"])
    async def error(self, ctx: commands.Context) -> None:
        """💥 Genera un mensaje de error falso y dramático."""
        await self._handle_ai_command(ctx, "error", "Finge que tienes un error")


async def setup(bot: commands.Bot) -> None:
    """Load the IA cog."""
    await bot.add_cog(IA(bot))
