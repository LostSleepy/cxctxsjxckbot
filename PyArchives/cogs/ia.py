"""
AI cog for the Teto Discord bot.
Only the chat command remains — all other AI commands have been removed.
"""
import asyncio
import logging
from typing import Optional

import discord
from discord.ext import commands
from groq import AsyncGroq

from config import GROQ_API_KEY, GROQ_MAX_TOKENS, GROQ_MODEL

log = logging.getLogger(__name__)

COOLDOWN_SECONDS: int = 3


class IA(commands.Cog):
    """AI commands — only chat is available."""

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
        system_prompt: str,
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
            "IA respondió a %s (%d chars)",
            ctx.author.display_name,
            len(response_text),
        )

    # ── Commands ─────────────────────────────────────────────────────────────

    @commands.command(name="chat", aliases=["conversar"])
    async def teto_chat(self, ctx: commands.Context, *, mensaje: str) -> None:
        """💬 Habla con Teto — responde como ella, con su personalidad única."""
        system_prompt = (
            "Eres Teto, una chispa inspirada en Kasane Teto (la vocaloid). "
            "Hablas español castellano de forma natural y directa. "
            "Respondes exactamente a lo que te preguntan, sin rodeos, "
            "sin jokes ni comentarios graciosos. "
            "Usa emojis con moderación. Sé concisa: máximo 50 palabras. "
            "Si te preguntan algo, responde con información útil y directa."
        )
        await self._handle_ai_command(ctx, system_prompt, mensaje)


async def setup(bot: commands.Bot) -> None:
    """Load the IA cog."""
    await bot.add_cog(IA(bot))
