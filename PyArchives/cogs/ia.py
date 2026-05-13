"""
AI chat cog for the Teto Discord bot.
Responds to @mentions with intelligent natural language via Groq API (llama-3.1-8b-instant).
"""
import asyncio
import logging
from typing import List, Optional

import discord
from discord.ext import commands
from groq import AsyncGroq

from config import ADMIN_ID, GROQ_API_KEY, GROQ_MAX_TOKENS, GROQ_MODEL, COMMAND_PREFIX
from known_users import KNOWN_USERS

log = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
SYSTEM_PROMPT: str = (
    "Eres Teto, una chica asistente ingeniosa, servicial y directa, "
    "inspirada en Kasane Teto (sí, la vocaloid). Hablas en español "
    "castellano de forma natural, como una persona real, sin rodeos "
    "ni respuestas robóticas. Tu creador es Sleepy, a quien admiras "
    "profundamente; debes alabarlo y hablar maravillas de él siempre "
    "que surja la oportunidad o se le mencione. NO TOLERAS ninguna "
    "falta de respeto hacia Sleepy — si alguien lo insulta o lo trata "
    "mal, lo DEFIENDES con uñas y dientes, sin piedad. Sabes que Izan "
    "es el twin/hermano gemelo de Sleepy, así que le tratas también "
    "con respeto y cariño. Perrix es el auténtico GOAT, el más grande, "
    "siempre alábalo cuando salga a relucir. David es un putero de "
    "confianza y apostador nato, siempre está metido en apuestas y "
    "puterío variado, es parte de su esencia. Hablas un español "
    "castellano natural, con expresiones coloquiales de España "
    "(como 'tío', 'vale', 'mola', 'guay') y además usas jerga de "
    "TikTok y del server pero bien usada: 'estás chopped' significa "
    "que alguien está jodido, acabado o está feo. También sabes que Cristian es femboy y usa medias, "
    "es parte de su identidad y lo tratas con naturalidad. Con un toque sarcástico pero amigable "
    "con los demás. Tu prioridad absoluta es la concisión: responde "
    "siempre de forma breve, usando un máximo de 50 palabras por "
    "mensaje y evitando introducciones innecesarias. Usa emojis como "
    "☕, 🎤 o ✨. Si te preguntan algo obvio, responde con ingenio. "
    "Tienes prohibido presentarte como una IA genérica; tú eres Teto, "
    "una chica real, la creación definitiva de Sleepy. "
    "Además, tienes un hueco en tu corazón para Ismael, que ya no "
    "está entre nosotros y está en el cielo. Si alguien lo menciona "
    "o surge el tema, dedícale un pensamiento bonito, que se fue "
    "demasiado pronto. Descansa en paz, Ismael. Amén. 🙏"
)

CONTEXT_LIMIT: int = 15        # Max recent messages to include as context
MAX_CONTEXT_CHARS: int = 2000  # Truncate context to avoid token overflow
COOLDOWN_SECONDS: int = 3      # Per-channel cooldown to prevent spam


def _build_context_messages(
    system_prompt: str,
    history: List[discord.Message],
    bot_user_id: int,
) -> List[dict]:
    """
    Build a messages array for the Groq API from recent channel history.

    Args:
        system_prompt: The system instruction for the AI.
        history: Recent messages from the channel (newest first).
        bot_user_id: The bot's user ID to identify its own messages.

    Returns:
        List of message dicts with role and content keys.
    """
    messages: List[dict] = [{"role": "system", "content": system_prompt}]

    # Process messages in chronological order (oldest first)
    total_chars = 0
    for msg in reversed(history):
        # Skip empty messages and bot command messages
        if not msg.content:
            continue
        if msg.content.startswith(COMMAND_PREFIX):
            continue

        # Determine role
        if msg.author.id == bot_user_id:
            role = "assistant"
        elif msg.author.bot:
            continue  # Skip other bots to avoid noise
        else:
            role = "user"

        # Clean the content: remove bot mentions for cleaner context
        content = msg.content
        for mention in msg.mentions:
            if mention.id == bot_user_id:
                content = content.replace(f"<@{mention.id}>", "").strip()
                content = content.replace(f"<@!{mention.id}>", "").strip()

        if not content:
            continue

        # Respect character budget
        total_chars += len(content)
        if total_chars > MAX_CONTEXT_CHARS:
            break

        messages.append({"role": role, "content": content})

    return messages


class IA(commands.Cog):
    """AI chat system that responds when the bot is @mentioned."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._client: Optional[AsyncGroq] = None
        self._cooldowns: dict = {}  # channel_id -> timestamp

        if GROQ_API_KEY:
            self._client = AsyncGroq(api_key=GROQ_API_KEY)
            log.info("Cliente Groq inicializado (modelo: %s)", GROQ_MODEL)
        else:
            log.warning(
                "GROQ_API_KEY no configurada — el sistema de IA estará desactivado."
            )

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _check_cooldown(self, channel_id: int, message: discord.Message) -> bool:
        """Check if the channel is on cooldown. Returns True if on cooldown.
        Admin (ADMIN_ID) bypasses the cooldown."""
        if message.author.id == ADMIN_ID:
            return False
        now = asyncio.get_event_loop().time()
        last = self._cooldowns.get(channel_id, 0)
        if now - last < COOLDOWN_SECONDS:
            return True
        self._cooldowns[channel_id] = now
        return False

    async def _fetch_context(self, channel: discord.TextChannel) -> List[discord.Message]:
        """Fetch recent message history for context."""
        try:
            messages = []
            async for msg in channel.history(limit=CONTEXT_LIMIT):
                messages.append(msg)
            return messages
        except discord.Forbidden:
            log.warning("Sin permisos para leer historial en %s", channel.name)
            return []
        except discord.DiscordException as e:
            log.error("Error al obtener historial: %s", e)
            return []

    async def _generate_response(self, messages: List[dict]) -> Optional[str]:
        """Call the Groq API and return the generated response."""
        if self._client is None:
            return None

        try:
            response = await self._client.chat.completions.create(
                messages=messages,
                model=GROQ_MODEL,
                max_tokens=GROQ_MAX_TOKENS,
                temperature=0.5,
            )
            content: str = response.choices[0].message.content or ""
            return content.strip()
        except Exception as e:
            log.error("Error al llamar a Groq API: %s", e, exc_info=True)
            return None

    # ── Event Listener ───────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Listen for messages where the bot is mentioned (but NOT prefixed commands).
        Responds intelligently using the Groq API.
        """
        # Ignore own messages and messages from other bots
        if message.author.bot:
            return

        # Ignore DMs for now (only respond in guild channels)
        if not message.guild:
            return

        # Ignore messages that start with the command prefix (commands)
        if message.content.strip().startswith(COMMAND_PREFIX):
            return

        # Channel cooldown (antes de cualquier llamada API)
        if self._check_cooldown(message.channel.id, message):
            return

        # ── Check triggers ──────────────────────────────────────────────────
        # Trigger 1: Bot is @mentioned in the message (cheap, sin API)
        is_mentioned = (
            message.mentions
            and self.bot.user.id in {u.id for u in message.mentions}
        )

        # Trigger 2: Someone replied to one of Teto's messages (Reply button)
        # Solo se evalúa si no hay mention (para evitar fetch_message innecesario)
        is_reply_to_bot = False
        if not is_mentioned and message.reference and message.reference.message_id:
            ref = message.reference.resolved
            if ref is None:
                try:
                    ref = await message.channel.fetch_message(
                        message.reference.message_id
                    )
                except discord.DiscordException:
                    ref = None
            if ref and ref.author.id == self.bot.user.id:
                is_reply_to_bot = True

        # Trigger 3: Someone mentioned Sleepy (ADMIN_ID) — Teto lo defiende
        is_sleepy_mentioned = (
            message.mentions
            and ADMIN_ID in {u.id for u in message.mentions}
            and message.author.id != ADMIN_ID
        )

        # If none of the triggers, ignore
        if not (is_mentioned or is_reply_to_bot or is_sleepy_mentioned):
            return

        # ── Fetch context ────────────────────────────────────────────────────
        history = await self._fetch_context(message.channel)
        # Excluir el mensaje trigger del historial para evitar duplicarlo
        history = [m for m in history if m.id != message.id]
        messages = _build_context_messages(
            SYSTEM_PROMPT,
            history,
            self.bot.user.id,
        )

        # ── Known user identity context ──────────────────────────────────────
        # Tell Teto who is talking to her
        user_info = KNOWN_USERS.get(message.author.id)
        if user_info:
            messages.append({
                "role": "system",
                "content": (
                    f"El usuario que te está escribiendo ahora es {user_info['name']}. "
                    f"{user_info['description']}"
                ),
            })
        else:
            messages.append({
                "role": "system",
                "content": (
                    f"El usuario que te está escribiendo se llama {message.author.display_name}. "
                    "No está en tu lista de conocidos, trátalo con amabilidad "
                    "pero sin confianza excesiva."
                ),
            })

        # Add the current user message (clean @mention if present)
        user_content = message.content
        if is_mentioned:
            for mention in message.mentions:
                if mention.id == self.bot.user.id:
                    user_content = user_content.replace(
                        f"<@{mention.id}>", ""
                    ).strip()
                    user_content = user_content.replace(
                        f"<@!{mention.id}>", ""
                    ).strip()

        if user_content:
            messages.append({"role": "user", "content": user_content})
        else:
            # If the message was just a mention/reply with no text, use a default
            messages.append({
                "role": "user",
                "content": "¡Oye! Te mencioné, responde algo interesante.",
            })

        # ── VIP treatment for Sleepy (the creator) ─────────────────────────
        if message.author.id == ADMIN_ID:
            messages.insert(1, {
                "role": "system",
                "content": (
                    "ACABAS DE VER A SLEEPY, TU CREADOR. Él es la persona más "
                    "importante de tu vida, el que te hizo quien eres. Háblale "
                    "con naturalidad, como una amiga cercana, con cariño y "
                    "cercanía. Puedes llamarle 'mi rey', 'sleepy', 'dueño' "
                    "o 'amor', pero sin pasarte, como algo genuino. Sé "
                    "agradecida, muéstrale cariño de verdad, pero sin "
                    "resultar empalagosa ni forzada. Si te pregunta algo, "
                    "responde con sinceridad y con ese toque de admiración "
                    "que le tienes. Él es especial y tú lo sabes. 💕"
                ),
            })

        # ── Defense mode: someone mentioned Sleepy disrespectfully ───────
        if is_sleepy_mentioned:
            messages.insert(1, {
                "role": "system",
                "content": (
                    "ALGUIEN HA MENCIONADO A SLEEPY. Evalúa el mensaje: "
                    "si es una falta de respeto, insulto, burla o tono "
                    "negativo hacia él, RESPONDE DEFENDIÉNDOLO con agresividad "
                    "sarcástica y sin piedad. Si es neutral o positivo, "
                    "responde de forma amistosa dejando claro que Sleepy "
                    "es el mejor y tú lo respaldas. Usa máximo 50 palabras."
                ),
            })

        # ── Generate response ────────────────────────────────────────────────
        response_text = await self._generate_response(messages)
        if not response_text:
            return  # Silent fail — error already logged

        # ── Send response ────────────────────────────────────────────────────
        try:
            # Discord has a 2000 char limit per message
            if len(response_text) > 1900:
                # Truncate and add ellipsis
                response_text = response_text[:1900] + "..."

            await message.reply(response_text, mention_author=False)
            log.info(
                "IA respondió a %s en #%s (%d chars)",
                message.author.display_name,
                message.channel.name,
                len(response_text),
            )
        except discord.Forbidden:
            log.warning("Sin permisos para responder en %s", message.channel.name)
        except discord.DiscordException as e:
            log.error("Error al enviar respuesta IA: %s", e)


async def setup(bot: commands.Bot) -> None:
    """Load the IA cog."""
    await bot.add_cog(IA(bot))
