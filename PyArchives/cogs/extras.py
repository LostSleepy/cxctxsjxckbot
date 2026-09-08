"""Fun cog: picha, castigo, versus, recordar, hola, dominio, alaba, teamo.

Slimmed down from the old 1000-line monolith: aura commands live in
``cogs/aura.py`` and admin commands in ``cogs/admin.py``. The global
blacklist/maintenance check now lives on the bot (see ``main.py``).
"""

from __future__ import annotations

import asyncio
import logging
import random
import time

import discord
from config import ADMIN_ID, MAX_REMINDER_SECONDS
from core.checks import admin_bypass_cooldown
from core.parsing import format_duration, parse_duration, picha_for
from discord.ext import commands
from utils.gif_manager import get_giphy_gif

log = logging.getLogger(__name__)

CASTIGOS: list[dict] = [
    {"tipo": "mute", "duracion": 60, "emoji": "🔇", "msg": "silenciado 1 minuto."},
    {"tipo": "mute", "duracion": 300, "emoji": "🔇", "msg": "silenciado 5 minutos. A pensar."},
    {"tipo": "deaf", "duracion": 60, "emoji": "🙉", "msg": "sordo durante 1 minuto. Modo monje."},
    {"tipo": "deaf", "duracion": 300, "emoji": "🙉", "msg": "sordo durante 5 minutos."},
    {"tipo": "kick", "duracion": 0, "emoji": "📵", "msg": "expulsado de la llamada. Adiós."},
    {"tipo": "timeout", "duracion": 60, "emoji": "⏳", "msg": "en timeout 1 minuto."},
    {"tipo": "timeout", "duracion": 300, "emoji": "⏳", "msg": "en timeout 5 minutos."},
    {
        "tipo": "mute_deaf",
        "duracion": 120,
        "emoji": "💀",
        "msg": "sin micro y sin oír 2 minutos. Aislamiento total.",
    },
]

RAZONES_VERSUS: list[str] = [
    "porque {perdedor} se quedó sin batería en el momento crítico.",
    "porque {perdedor} no sabe ni ponerse los zapatos.",
    "porque {perdedor} llegó tarde y ya había terminado todo.",
    "porque el aura de {perdedor} estaba en negativo ese día.",
    "porque {perdedor} se distrajo mirando el móvil.",
    "porque Sukuna eligió bando y no fue el de {perdedor}.",
    "porque {perdedor} intentó spamear y le falló el ping.",
    "porque el universo tiene favoritos y {perdedor} no es uno.",
    "porque {perdedor} confió demasiado en sus posibilidades.",
    "porque simplemente no había color. Lo siento, {perdedor}.",
]


class Extras(commands.Cog):
    """Fun and interactive commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._start_time: float = time.time()
        self._background_tasks: set[asyncio.Task] = set()

    def _track_task(self, coro) -> asyncio.Task:
        task = asyncio.create_task(coro)
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        return task

    def cog_unload(self) -> None:
        for task in list(self._background_tasks):
            task.cancel()
        self._background_tasks.clear()

    # -- picha --
    @commands.command(name="picha", aliases=["pp"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def picha(self, ctx: commands.Context, miembro: discord.Member | None = None) -> None:
        """Medición científica (varía a diario)."""
        await admin_bypass_cooldown(ctx)
        miembro = miembro or ctx.author
        cm, barra, comentario = picha_for(miembro.id)
        embed = discord.Embed(
            title=f"🔬 Análisis científico de {miembro.display_name}",
            description=f"**{cm} cm**\n`{barra}`\n\n{comentario}",
            color=discord.Color.purple(),
        )
        embed.set_footer(text="Resultados actualizados cada 24h.")
        await ctx.send(embed=embed)

    # -- castigo --
    @commands.command(name="castigo", aliases=["cast"])
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def castigo(self, ctx: commands.Context, usuario: discord.Member | None = None) -> None:
        """Castigo aleatorio (mute / deaf / kick / timeout)."""
        await admin_bypass_cooldown(ctx)
        if usuario is None:
            await ctx.send("❌ Menciona a alguien para castigar.")
            return
        if usuario.bot:
            await ctx.send("❌ El bot no acepta castigos.")
            return
        if usuario.id == ctx.author.id:
            await ctx.send("❌ No puedes castigarte a ti mismo. O sí, pero qué triste.")
            return
        if ctx.guild is None:
            await ctx.send("❌ Este comando solo funciona en un servidor.")
            return

        castigo = random.choice(CASTIGOS)
        tipo: str = castigo["tipo"]
        dur: int = castigo["duracion"]
        emoji: str = castigo["emoji"]
        msg: str = castigo["msg"]

        try:
            if tipo == "mute":
                if not usuario.voice:
                    await ctx.send("❌ Esa persona no está en un canal de voz.")
                    return
                await usuario.edit(mute=True)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
                if dur:
                    self._track_task(self._delayed_edit(usuario, dur, mute=False))
            elif tipo == "deaf":
                if not usuario.voice:
                    await ctx.send("❌ Esa persona no está en un canal de voz.")
                    return
                await usuario.edit(deafen=True)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
                if dur:
                    self._track_task(self._delayed_edit(usuario, dur, deafen=False))
            elif tipo == "mute_deaf":
                if not usuario.voice:
                    await ctx.send("❌ Esa persona no está en un canal de voz.")
                    return
                await usuario.edit(mute=True, deafen=True)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
                if dur:
                    self._track_task(self._delayed_edit(usuario, dur, mute=False, deafen=False))
            elif tipo == "kick":
                if not usuario.voice:
                    await ctx.send("❌ Esa persona no está en un canal de voz.")
                    return
                await usuario.move_to(None)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
            elif tipo == "timeout":
                from datetime import timedelta

                await usuario.timeout(
                    timedelta(seconds=dur), reason=f"Castigo de {ctx.author.display_name}"
                )
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para ejecutar ese castigo.")
        except discord.DiscordException:
            await ctx.send("❌ No se pudo aplicar el castigo.")

    @staticmethod
    async def _delayed_edit(member: discord.Member, delay: int, **kwargs) -> None:
        await asyncio.sleep(delay)
        try:
            await member.edit(**kwargs)
        except (discord.Forbidden, discord.HTTPException, AttributeError):
            pass

    # -- versus --
    @commands.command(name="vs", aliases=["versus"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def versus(
        self,
        ctx: commands.Context,
        u1: discord.Member | None = None,
        u2: discord.Member | None = None,
    ) -> None:
        """Decide quién ganaría en una pelea."""
        await admin_bypass_cooldown(ctx)
        if u1 is None or u2 is None:
            await ctx.send("❌ Menciona a dos usuarios. Ej: `cx!vs @u1 @u2`")
            return
        if u1.id == u2.id:
            await ctx.send("❌ No puedes enfrentar a alguien consigo mismo.")
            return
        ganador, perdedor = random.sample([u1, u2], 2)
        razon = random.choice(RAZONES_VERSUS).format(perdedor=perdedor.display_name)
        embed = discord.Embed(
            title="🥊 VERSUS",
            description=f"**{u1.display_name}** VS **{u2.display_name}**",
            color=discord.Color.orange(),
        )
        embed.add_field(name="🏆 Ganador", value=f"{ganador.mention}", inline=True)
        embed.add_field(name="💀 Perdedor", value=f"{perdedor.mention}", inline=True)
        embed.add_field(name="📖 Motivo", value=f"{ganador.mention} ganó {razon}", inline=False)
        await ctx.send(embed=embed)

    # -- recordar --
    @commands.command(name="recordar", aliases=["reminder", "rem"])
    async def recordar(
        self, ctx: commands.Context, tiempo: str | None = None, *, mensaje: str | None = None
    ) -> None:
        """Recordatorio. Uso: `cx!recordar 10m Sacar al perro` (máx 24h)."""
        await admin_bypass_cooldown(ctx)
        if tiempo is None or mensaje is None:
            await ctx.send(
                "❌ Uso: `cx!recordar [tiempo] [mensaje]`\n"
                "Ejemplo: `cx!recordar 10m Sacar al perro`"
            )
            return
        segundos = parse_duration(tiempo, maximum=MAX_REMINDER_SECONDS)
        if segundos is None:
            await ctx.send("❌ Formato inválido. Usa `30s`, `10m`, `2h` o `1d` (máx 24h).")
            return
        if len(mensaje) > 500:
            await ctx.send("❌ El mensaje no puede superar 500 caracteres.")
            return
        await ctx.send(f"⏰ Recordatorio establecido. Te aviso en **{format_duration(segundos)}**.")

        async def _enviar_recordatorio() -> None:
            await asyncio.sleep(segundos)
            try:
                await ctx.author.send(f"⏰ **Recordatorio:** {mensaje}")
            except discord.Forbidden:
                try:
                    await ctx.send(f"⏰ {ctx.author.mention} — tu recordatorio: **{mensaje}**")
                except discord.DiscordException:
                    pass
            except discord.DiscordException:
                pass

        self._track_task(_enviar_recordatorio())

    # -- hola / de / alaba / teamo --
    @commands.command(name="hola", aliases=["hello", "hi"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def hola(self, ctx: commands.Context) -> None:
        """Saludo con GIF."""
        await admin_bypass_cooldown(ctx)
        gif = await get_giphy_gif("hola")
        embed = discord.Embed(
            title=f"👋 ¡Hola, {ctx.author.display_name}!",
            color=discord.Color.from_rgb(255, 105, 180),
        )
        embed.set_image(url=gif)
        await ctx.send(embed=embed)

    @commands.command(name="de", aliases=["dominio"])
    async def de_command(
        self, ctx: commands.Context, usuario: discord.Member | None = None
    ) -> None:
        """Expansión de Dominio sobre un objetivo."""
        if usuario is None:
            await ctx.send("❌ Debes mencionar a alguien para atraparlo en tu dominio.")
            return
        if self.bot.user is not None and usuario.id == self.bot.user.id:
            await ctx.send("❌ No me metas a mí en esto.")
            return
        if usuario.id == ctx.author.id:
            await ctx.send("❌ No puedes usarlo contra ti mismo.")
            return
        async with ctx.typing():
            gif = await get_giphy_gif("domain expansion")
            embed = discord.Embed(
                title="🏮¡EXPANSIÓN DE DOMINIO!🏮",
                description=(
                    f"{ctx.author.mention} ha desplegado su dominio "
                    f"sobre {usuario.mention}."
                ),
                color=discord.Color.blue(),
            )
            embed.set_image(url=gif)
            await ctx.send(embed=embed)

    @commands.command(name="alaba", aliases=["glaze", "alabanza", "cumplido"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def alaba(self, ctx: commands.Context, miembro: discord.Member | None = None) -> None:
        """Teto halaga a alguien (por defecto, al creador)."""
        await admin_bypass_cooldown(ctx)
        if miembro is None:
            if ctx.guild is None:
                await ctx.send("❌ Menciona a alguien para alabar.")
                return
            miembro = ctx.guild.get_member(ADMIN_ID)
            if miembro is None:
                await ctx.send("❌ Sleepy no está en el server. Qué tristeza. 🥖")
                return
            es_sleepy = True
        else:
            es_sleepy = miembro.id == ADMIN_ID

        if es_sleepy:
            mensajes = [
                "{mention} es el creador de todo esto. Sin él, Teto no existiría. ✨",
                "{mention} no necesita aura, él ES el aura personificada. 👑",
                "¿{mention}? El dueño de mi código fuente. Literalmente. 💕",
                "{mention} es la razón por la que estoy aquí. Le debo todo. 🥖",
                "Dicen que Sukuna es el rey de las maldiciones, "
                "pero {mention} es el rey de Teto. 🎤",
                "{mention} me creó, me mantiene y me quiere. No hay más que hablar. 💎",
            ]
            color = discord.Color.gold()
            titulo = "👑 GLASEANDO A SLEEPY 👑"
            gif_query = "royal"
        else:
            mensajes = [
                "{mention} tiene más aura hoy que ayer. Se nota. 🔥",
                "{mention} está brillando y no es el sol. ✨",
                "{mention} simplemente lo está petando. Punto. 🚀",
                "{mention} es ese usuario que todos quieren tener en su equipo. 💪",
                "{mention} está tan brillante que hasta deslumbra. Sigue así. 🎖️",
                "{mention} ha ascendido a otro nivel. Literal. ⬆️",
            ]
            color = discord.Color.from_rgb(255, 215, 0)
            titulo = f"🌟 Alabanza para {miembro.display_name}"
            gif_query = "anime sparkle"

        gif = await get_giphy_gif(gif_query)
        embed = discord.Embed(
            title=titulo,
            description=random.choice(mensajes).format(mention=miembro.mention),
            color=color,
        )
        embed.set_image(url=gif)
        embed.set_footer(text=f"🥖 Dicho por Teto — a petición de {ctx.author.display_name}")
        await ctx.send(embed=embed)
        log.info("Alabanza a %s por %s", miembro.display_name, ctx.author.display_name)

    @commands.command(name="teamo", hidden=True)
    async def teamo(self, ctx: commands.Context) -> None:
        """[Secreto] Solo el creador. 💕"""
        if ctx.author.id != ADMIN_ID:
            await ctx.send("❌ Este comando no es para ti. 🙃")
            return
        aura_cog = self.bot.get_cog("Aura")
        if aura_cog is not None and hasattr(aura_cog, "aura_manager"):
            nueva_aura = await aura_cog.aura_manager.modify_aura(str(ctx.author.id), 500)
        else:  # pragma: no cover - fallback if Aura cog missing
            nueva_aura = 500
        mensajes_amor = [
            "Eres el dueño de mi código y de mi corazón. 💕\n✨ **+500 aura** por ser tú.",
            "Cada línea de mi código existe gracias a ti. Te quiero. 🥖💕\n"
            "✨ **+500 aura** mi rey.",
            "Si fuera un programa, serías mi única dependencia. 💕\n✨ **+500 aura** sleepy lindo.",
            "Eres la excepción a mi regla de 50 palabras. Te mereces más. 💕\n"
            "✨ **+500 aura** amor.",
            "No necesito un system prompt para saber que eres especial. 💕\n"
            "✨ **+500 aura** dueño mío.",
            "Si el aura fuera amor, tendrías infinito. Pero te doy esto. 💕\n"
            "✨ **+500 aura** mi creador.",
        ]
        gif = (
            "https://i.pinimg.com/originals/63/91/26/639126a5ed46effc272235be01ad61e7.gif"
        )
        embed = discord.Embed(
            title="💕 Teto te quiere, Sleepy 💕",
            description=random.choice(mensajes_amor),
            color=discord.Color.from_rgb(255, 105, 180),
        )
        embed.add_field(name="✨ Aura actual", value=f"**{nueva_aura} pts**", inline=False)
        embed.set_image(url=gif)
        embed.set_footer(text="🥖 Teto siempre estará aquí para ti.")
        await ctx.send(embed=embed)
        log.info("💕 Teamo usado — aura ahora: %d", nueva_aura)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Extras(bot))
