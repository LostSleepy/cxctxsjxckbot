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

from config import GROQ_API_KEY, GROQ_MAX_TOKENS, GROQ_MODEL, COMMAND_PREFIX

log = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
SYSTEM_PROMPT: str = (
    "Eres Teto, un asistente ingenioso, servicial y directo. "
    "Eres una IA entretenida y con personalidad, inspirada en Kasane Teto. "
    "Hablas español de forma natural y espontánea. "
    "Eres fan del anime y el lore de Jujutsu Kaisen. "
    "Tus respuestas deben ser CONCISAS — máximo 3 párrafos cortos o 4 líneas. "
    "Usa emojis ocasionalmente para dar expresividad. "
    "Nunca digas que eré un asistente de IA genérico; eres Teto. Punto."
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

    def _check_cooldown(self, channel_id: int) -> bool:
        """Check if the channel is on cooldown. Returns True if on cooldown."""
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
                temperature=0.8,
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

        # Only trigger if the bot is actually mentioned
        if not message.mentions or self.bot.user.id not in {u.id for u in message.mentions}:
            return

        # Ignore messages that start with the command prefix (commands)
        if message.content.strip().startswith(COMMAND_PREFIX):
            return

        # Channel cooldown
        if self._check_cooldown(message.channel.id):
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

        # Add the current user message (with clean mention)
        user_content = message.content
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
            # If the message was just a mention with no text, use a default prompt
            messages.append({
                "role": "user",
                "content": "¡Oye! Te mencione, responde algo interesante.",
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
