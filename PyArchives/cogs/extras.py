"""
Extras cog — fun and interactive commands for the Teto Discord bot.
Includes the Aura system, GIF commands (Black Flash, Domain Expansion),
voting, reminders, and more.
"""
import asyncio
import json
import logging
import os
import platform
import random
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import List, Optional, Tuple

import discord
from discord.ext import commands

from config import ADMIN_ID, AURA_DATA_PATH, BLACKLIST_PATH, CANAL_ANUNCIOS_ID, MAINTENANCE_PATH, VOTOS_CHOPPED_PATH
from utils.aura_manager import AuraManager
from utils.gif_manager import get_aura_gif, get_giphy_gif

log = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────

MENSAJES_CHOPPED: List[str] = [
    "estás super chopped {mention} 💀",
    "{mention} eres un chopped de manual, lo siento.",
    "alguien tenía que decírtelo... {mention}, estás chopped.",
    "{mention} chopped detected. 🚨",
    "el bot ha decidido: {mention} está chopped hoy.",
    "{mention} ni el aura te salva, estás chopped. 📉",
    "aviso a la comunidad: {mention} está chopped. Proceded con cautela.",
    "{mention} ¿tú bien? porque el bot dice que no. Chopped total.",
    "análisis completado. Resultado: {mention} — chopped. 🔬",
    "{mention} te ha tocado. Estás chopped, asúmelo.",
]

MENSAJES_BF_RECORD: List[str] = [
    "⚡⚡⚡ **RÉCORD DE DESTELLOS NEGROS** ⚡⚡⚡\n"
    "{mention} ha encadenado Destellos consecutivos. "
    "Aura **duplicada** a **{aura} pts**. Histórico.",
    "⚡ **DESTELLO NEGRO PERFECTO** ⚡\n"
    "{mention} ha rozado lo imposible. Su aura explota hasta **{aura} pts**.",
    "💥 **CONVERGENCIA DE ENERGÍA MALDITA** 💥\n"
    "{mention} lo ha hecho. Aura **x2** — ahora en **{aura} pts**. "
    "El server tiembla.",
]

CASTIGOS: List[dict] = [
    {"tipo": "mute", "duracion": 60, "emoji": "🔇", "msg": "silenciado 1 minuto."},
    {"tipo": "mute", "duracion": 300, "emoji": "🔇", "msg": "silenciado 5 minutos. A pensar."},
    {"tipo": "deaf", "duracion": 60, "emoji": "🙉", "msg": "sordo durante 1 minuto. Modo monje."},
    {"tipo": "deaf", "duracion": 300, "emoji": "🙉", "msg": "sordo durante 5 minutos."},
    {"tipo": "kick", "duracion": 0, "emoji": "📵", "msg": "expulsado de la llamada. Adiós."},
    {"tipo": "timeout", "duracion": 60, "emoji": "⏳", "msg": "en timeout 1 minuto."},
    {"tipo": "timeout", "duracion": 300, "emoji": "⏳", "msg": "en timeout 5 minutos."},
    {"tipo": "mute_deaf", "duracion": 120, "emoji": "💀", "msg": "sin micro y sin oír 2 minutos. Aislamiento total."},
]

RAZONES_VERSUS: List[str] = [
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


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_tiempo_reminder(tiempo: str) -> Optional[int]:
    """
    Parse a time string like '10m', '2h', '30s' into seconds.

    Args:
        tiempo: Time string with suffix (s, m, h).

    Returns:
        Seconds as int, or None if invalid.
    """
    if not tiempo:
        return None
    unidad = tiempo[-1].lower()
    try:
        valor = int(tiempo[:-1])
    except ValueError:
        return None

    multipliers = {"s": 1, "m": 60, "h": 3600}
    mult = multipliers.get(unidad)
    if mult is None:
        return None
    return valor * mult


def _cargar_votos(votos_path: Path) -> dict:
    """Load chopped votes from JSON file."""
    if not votos_path.exists():
        return {}
    try:
        with open(votos_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _guardar_votos(data: dict, votos_path: Path) -> None:
    """Save chopped votes to JSON file atomically."""
    temp = votos_path.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp.replace(votos_path)


def _limpiar_votos_expirados(votos: dict, ahora: float) -> None:
    """Remove votes older than 5 minutes from the data."""
    for uid in list(votos.keys()):
        votos[uid] = [
            (vid, ts) for vid, ts in votos[uid] if ahora - ts < 300
        ]
        if not votos[uid]:
            del votos[uid]


def _generar_picha(user_id: int) -> Tuple[int, str, str]:
    """
    Generate a scientifically accurate picha measurement.
    Uses a seed based on user ID and current day for consistency.

    Returns:
        Tuple of (cm, bar, comment).
    """
    r = random.Random(user_id + int(time.time() // 86400))
    cm = r.randint(0, 30)
    barra = "8" + "=" * cm + "D"

    if cm >= 20:
        comentario = "Dios mío. 😳"
    elif cm >= 12:
        comentario = "Respetable."
    elif cm >= 6:
        comentario = "Normal tirando a normal."
    else:
        comentario = "Hay que rezar."

    return cm, barra, comentario


# ── Cog ────────────────────────────────────────────────────────────────────────

class Extras(commands.Cog):
    """
    Fun and interactive commands: Aura system, battles, voting, reminders, etc.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.aura_manager = AuraManager(AURA_DATA_PATH)
        self._votos_chopped: dict = _cargar_votos(VOTOS_CHOPPED_PATH)
        self._start_time: float = time.time()
        self._blacklist: set[str] = self._load_blacklist()
        self._maintenance: bool = self._load_maintenance()
        # Hold strong refs to background tasks (castigo unmuters + recordar)
        # so they aren't GC'd mid-execution.
        self._background_tasks: set[asyncio.Task] = set()
        # Global check: block blacklisted users & maintenance mode
        self._bound_check = self._blacklist_check
        self.bot.add_check(self._bound_check)

    def _track_task(self, coro) -> asyncio.Task:
        """Create and retain a strong reference to a background task.

        Without this, asyncio may collect the task before it actually
        completes (see https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task).
        The discard callback removes the ref once the task finishes.
        """
        task = asyncio.create_task(coro)
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        return task

    def _load_blacklist(self) -> set[str]:
        """Load blacklisted user IDs from JSON."""
        if not BLACKLIST_PATH.exists():
            return set()
        try:
            with open(BLACKLIST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return set(data.get("blocked", []))
        except (json.JSONDecodeError, OSError):
            return set()

    def _save_blacklist(self) -> None:
        """Save blacklisted user IDs to JSON atomically."""
        temp = BLACKLIST_PATH.with_suffix(".tmp")
        with open(temp, "w", encoding="utf-8") as f:
            json.dump({"blocked": list(self._blacklist)}, f, indent=2)
        temp.replace(BLACKLIST_PATH)

    def _load_maintenance(self) -> bool:
        """Load maintenance mode state from JSON."""
        if not MAINTENANCE_PATH.exists():
            return False
        try:
            with open(MAINTENANCE_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("enabled", False)
        except (json.JSONDecodeError, OSError):
            return False

    def _save_maintenance(self) -> None:
        """Save maintenance mode state to JSON atomically."""
        temp = MAINTENANCE_PATH.with_suffix(".tmp")
        with open(temp, "w", encoding="utf-8") as f:
            json.dump({"enabled": self._maintenance}, f, indent=2)
        temp.replace(MAINTENANCE_PATH)

    async def _blacklist_check(self, ctx: commands.Context) -> bool:
        """Global check: block blacklisted users & maintenance mode."""
        # Admin is never blocked
        if ctx.author.id == ADMIN_ID:
            return True
        if str(ctx.author.id) in self._blacklist:
            await ctx.send(
                "🚫 Estás bloqueado y no puedes usar comandos del bot.",
                delete_after=5,
            )
            return False
        if self._maintenance:
            await ctx.send(
                "⚙️ Teto está en **mantenimiento**. Prueba más tarde.",
                delete_after=8,
            )
            return False
        return True

    async def cog_unload(self) -> None:
        """Remove the global check when the cog is unloaded."""
        try:
            self.bot.remove_check(self._bound_check)
        except Exception:
            pass

    # ── Admin Cooldown Bypass ────────────────────────────────────────────────
    async def _bypass_cooldown(self, ctx: commands.Context) -> None:
        """Remove cooldown for the configured admin."""
        if ctx.author.id == ADMIN_ID:
            ctx.command.reset_cooldown(ctx)

    # ── Chopped Daily (command) ─────────────────────────────────────────────
    @commands.command(
        name="choppeddaily",
        aliases=["cd", "chopped", "dailychopped"],
    )
    async def chopped_daily(self, ctx: commands.Context) -> None:
        """
        Pick a random server member and publicly declare them chopped.
        The ritual cannot be stopped. 🥖
        """
        canal = self.bot.get_channel(CANAL_ANUNCIOS_ID)
        if canal is None:
            await ctx.send("❌ No encuentro el canal de anuncios.")
            return

        guild = ctx.guild
        humanos = [m for m in guild.members if not m.bot]
        if not humanos:
            await ctx.send("❌ No hay humanos que choppear aquí.")
            return

        elegido = random.choice(humanos)
        mensaje = random.choice(MENSAJES_CHOPPED).format(mention=elegido.mention)
        await canal.send(mensaje)
        log.info("Chopped diario: %s (por %s)", elegido.display_name, ctx.author.display_name)

    # ── AURA ─────────────────────────────────────────────────────────────────
    @commands.command(name="aura")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def aura(
        self,
        ctx: commands.Context,
        miembro: Optional[discord.Member] = None,
    ) -> None:
        """Check your daily aura score (resets every 24h)."""
        await self._bypass_cooldown(ctx)
        miembro = miembro or ctx.author
        puntos = await self.aura_manager.get_aura(str(miembro.id))

        embed = discord.Embed(
            title=f"✨ Aura de {miembro.display_name}",
            description=self.aura_manager.get_aura_message(puntos),
            color=discord.Color.gold() if puntos >= 0 else discord.Color.dark_red(),
        )
        embed.set_image(url=await get_aura_gif(puntos))
        embed.set_footer(text="Se resetea cada 24h.")
        await ctx.send(embed=embed)

    # ── Top Aura ─────────────────────────────────────────────────────────────
    @commands.command(name="top", aliases=["ranking", "leaderboard"])
    async def top_aura(self, ctx: commands.Context) -> None:
        """Show the server's aura ranking (top 10)."""
        await self._bypass_cooldown(ctx)
        guild_member_ids = {str(m.id) for m in ctx.guild.members if not m.bot}
        ranking = await self.aura_manager.get_top_aura(guild_member_ids, limit=10)

        if not ranking:
            await ctx.send("📊 Nadie ha consultado su aura hoy todavía.")
            return

        medallas = ["🥇", "🥈", "🥉"] + ["🔹"] * 7
        lineas: List[str] = []
        for i, (uid, puntos) in enumerate(ranking):
            nombre = ctx.guild.get_member(int(uid))
            display = nombre.display_name if nombre else f"ID:{uid}"
            lineas.append(f"{medallas[i]} **{display}** — {puntos} pts")

        embed = discord.Embed(
            title="📊 Ranking de Aura — Top 10",
            description="\n".join(lineas),
            color=discord.Color.gold(),
        )
        embed.set_footer(text="Solo usuarios que han consultado su aura hoy.")
        await ctx.send(embed=embed)

    # ── Picha ────────────────────────────────────────────────────────────────
    @commands.command(name="picha", aliases=["pp"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def picha(
        self,
        ctx: commands.Context,
        miembro: Optional[discord.Member] = None,
    ) -> None:
        """Scientific measurement. Results vary daily."""
        await self._bypass_cooldown(ctx)
        miembro = miembro or ctx.author
        cm, barra, comentario = _generar_picha(miembro.id)

        embed = discord.Embed(
            title=f"🔬 Análisis científico de {miembro.display_name}",
            description=f"**{cm} cm**\n`{barra}`\n\n{comentario}",
            color=discord.Color.purple(),
        )
        embed.set_footer(text="Resultados actualizados cada 24h.")
        await ctx.send(embed=embed)

    # ── Vote Chopped ─────────────────────────────────────────────────────────
    @commands.command(name="vc", aliases=["votochopped"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def voto_chopped(
        self,
        ctx: commands.Context,
        usuario: Optional[discord.Member] = None,
    ) -> None:
        """
        Vote to chopped someone. 3 votes within 5 min = 5 min timeout.
        Votes are persisted across bot restarts.
        """
        await self._bypass_cooldown(ctx)
        if usuario is None:
            await ctx.send("❌ Menciona a alguien para votar.")
            return
        if usuario.bot:
            await ctx.send("❌ No puedes votar contra el bot.")
            return
        if usuario.id == ctx.author.id:
            await ctx.send("❌ No puedes votarte a ti mismo.")
            return

        ahora = time.time()
        vid = str(usuario.id)
        _limpiar_votos_expirados(self._votos_chopped, ahora)

        # Check if user already voted against this person
        votantes_actuales = {uid for uid, _ in self._votos_chopped.get(vid, [])}
        if ctx.author.id in votantes_actuales:
            await ctx.send("❌ Ya has votado contra esta persona recientemente.")
            return

        # Register vote
        if vid not in self._votos_chopped:
            self._votos_chopped[vid] = []
        self._votos_chopped[vid].append((ctx.author.id, ahora))
        _guardar_votos(self._votos_chopped, VOTOS_CHOPPED_PATH)

        total = len(self._votos_chopped[vid])

        if total >= 3:
            # Reset votes for this user
            self._votos_chopped[vid] = []
            _guardar_votos(self._votos_chopped, VOTOS_CHOPPED_PATH)

            if not ctx.guild.me.guild_permissions.moderate_members:
                await ctx.send("❌ Me falta el permiso `Moderate Members`.")
                return

            try:
                await usuario.timeout(
                    timedelta(minutes=5),
                    reason=f"Voto Chopped de {ctx.author}.",
                )
                await ctx.send(
                    f"💀 **CHOPPED.** {usuario.mention} silenciado 5 minutos."
                )
            except discord.Forbidden:
                await ctx.send(
                    "❌ No tengo permisos para silenciar a esa persona."
                )
        else:
            await ctx.send(
                f"🗳️ Voto contra {usuario.mention}. "
                f"**{total}/3** — faltan {3 - total}."
            )

    # ── Castigo (non-blocking) ───────────────────────────────────────────────
    @commands.command(name="castigo", aliases=["cast"])
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def castigo(
        self,
        ctx: commands.Context,
        usuario: Optional[discord.Member] = None,
    ) -> None:
        """
        Sentence someone to a random punishment.
        Uses non-blocking background tasks for timed unmutes.
        """
        await self._bypass_cooldown(ctx)
        if usuario is None:
            await ctx.send("❌ Menciona a alguien para castigar.")
            return
        if usuario.bot:
            await ctx.send("❌ El bot no acepta castigos.")
            return
        if usuario.id == ctx.author.id:
            await ctx.send(
                "❌ No puedes castigarte a ti mismo. O sí, pero qué triste."
            )
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
                    self._track_task(
                        self._delayed_edit(usuario, dur, mute=False)
                    )

            elif tipo == "deaf":
                if not usuario.voice:
                    await ctx.send("❌ Esa persona no está en un canal de voz.")
                    return
                await usuario.edit(deafen=True)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
                if dur:
                    self._track_task(
                        self._delayed_edit(usuario, dur, deafen=False)
                    )

            elif tipo == "mute_deaf":
                if not usuario.voice:
                    await ctx.send("❌ Esa persona no está en un canal de voz.")
                    return
                await usuario.edit(mute=True, deafen=True)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
                if dur:
                    self._track_task(
                        self._delayed_edit(usuario, dur, mute=False, deafen=False)
                    )

            elif tipo == "kick":
                if not usuario.voice:
                    await ctx.send("❌ Esa persona no está en un canal de voz.")
                    return
                await usuario.move_to(None)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")

            elif tipo == "timeout":
                await usuario.timeout(
                    timedelta(seconds=dur),
                    reason=f"Castigo de {ctx.author.display_name}",
                )
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")

        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para ejecutar ese castigo.")

    @staticmethod
    async def _delayed_edit(
        member: discord.Member,
        delay: int,
        **kwargs,
    ) -> None:
        """
        Apply edit to a member after a delay (non-blocking background task).
        Used for auto-unmute/undeafen after castigos.
        """
        await asyncio.sleep(delay)
        try:
            await member.edit(**kwargs)
        except (discord.Forbidden, discord.HTTPException, AttributeError):
            pass

    # ── Versus ───────────────────────────────────────────────────────────────
    @commands.command(name="vs", aliases=["versus"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def versus(
        self,
        ctx: commands.Context,
        u1: Optional[discord.Member] = None,
        u2: Optional[discord.Member] = None,
    ) -> None:
        """Decide who would win in a fight between two users."""
        await self._bypass_cooldown(ctx)
        if u1 is None or u2 is None:
            await ctx.send(
                "❌ Menciona a dos usuarios. Ej: `cx!vs @u1 @u2`"
            )
            return
        if u1.id == u2.id:
            await ctx.send("❌ No puedes enfrentar a alguien consigo mismo.")
            return

        ganador, perdedor = random.sample([u1, u2], 2)
        razon = random.choice(RAZONES_VERSUS).format(
            perdedor=perdedor.display_name
        )

        embed = discord.Embed(
            title="🥊 VERSUS",
            description=f"**{u1.display_name}** VS **{u2.display_name}**",
            color=discord.Color.orange(),
        )
        embed.add_field(name="🏆 Ganador", value=f"{ganador.mention}", inline=True)
        embed.add_field(name="💀 Perdedor", value=f"{perdedor.mention}", inline=True)
        embed.add_field(
            name="📖 Motivo",
            value=f"{ganador.mention} ganó {razon}",
            inline=False,
        )
        await ctx.send(embed=embed)

    # ── Recordar ─────────────────────────────────────────────────────────────
    @commands.command(name="recordar", aliases=["reminder", "rem"])
    async def recordar(
        self,
        ctx: commands.Context,
        tiempo: Optional[str] = None,
        *,
        mensaje: Optional[str] = None,
    ) -> None:
        """
        Set a reminder.
        Usage: cx!recordar 10m Sacar al perro
        """
        await self._bypass_cooldown(ctx)
        if tiempo is None or mensaje is None:
            await ctx.send(
                "❌ Uso: `cx!recordar [tiempo] [mensaje]`\n"
                "Ejemplo: `cx!recordar 10m Sacar al perro`"
            )
            return

        segundos = _parse_tiempo_reminder(tiempo)
        if segundos is None:
            await ctx.send(
                "❌ Formato de tiempo inválido. Usa `10m`, `2h` o `30s`."
            )
            return

        if segundos > 86400:
            await ctx.send("❌ Máximo 24 horas de recordatorio.")
            return

        await ctx.send(f"⏰ Recordatorio establecido. Te aviso en **{tiempo}**.")

        async def _enviar_recordatorio() -> None:
            """Send the reminder after the delay."""
            await asyncio.sleep(segundos)
            try:
                await ctx.author.send(f"⏰ **Recordatorio:** {mensaje}")
            except discord.Forbidden:
                await ctx.send(
                    f"⏰ {ctx.author.mention} — tu recordatorio: **{mensaje}**"
                )

        self._track_task(_enviar_recordatorio())

    # ── Black Flash ──────────────────────────────────────────────────────────
    @commands.command(name="bf", aliases=["blackflash"])
    async def bf_command(
        self,
        ctx: commands.Context,
        usuario: Optional[discord.Member] = None,
    ) -> None:
        """
        Launch a Black Flash at a user.
        5% chance to double your aura (announced in announcements channel).
        """
        if usuario is None:
            await ctx.send("❌ Debes mencionar a alguien para darle un Black Flash.")
            return
        if usuario.id == self.bot.user.id:
            await ctx.send("❌ No me metas a mí en esto.")
            return
        if usuario.id == ctx.author.id:
            await ctx.send("❌ No puedes usarlo contra ti mismo.")
            return

        async with ctx.typing():
            gif = await get_giphy_gif("black flash")
            embed = discord.Embed(
                title="⚡¡Black Flash!⚡",
                description=(
                    f"{ctx.author.mention} le ha propinado un "
                    f"**Destello Negro** a {usuario.mention}."
                ),
                color=discord.Color.red(),
            )
            embed.set_image(url=gif)
            await ctx.send(embed=embed)

        # 5% chance to double aura
        if random.random() < 0.05:
            uid = str(ctx.author.id)
            existing = await self.aura_manager.get_aura_if_exists(uid)
            if existing is not None:
                nueva = existing * 2
            else:
                nueva = 100
            await self.aura_manager.set_aura(uid, nueva)

            canal = self.bot.get_channel(CANAL_ANUNCIOS_ID)
            if canal:
                mensaje = random.choice(MENSAJES_BF_RECORD).format(
                    mention=ctx.author.mention,
                    aura=nueva,
                )
                await canal.send(mensaje)

    # ── Hola ─────────────────────────────────────────────────────────────────
    @commands.command(name="hola", aliases=["hello", "hi"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def hola(self, ctx: commands.Context) -> None:
        """Greeting with a random GIF."""
        await self._bypass_cooldown(ctx)
        gif = await get_giphy_gif("hola")
        embed = discord.Embed(
            title=f"👋 ¡Hola, {ctx.author.display_name}!",
            color=discord.Color.from_rgb(255, 105, 180),
        )
        embed.set_image(url=gif)
        await ctx.send(embed=embed)

    # ── Domain Expansion ─────────────────────────────────────────────────────
    @commands.command(name="de", aliases=["dominio"])
    async def de_command(
        self,
        ctx: commands.Context,
        usuario: Optional[discord.Member] = None,
    ) -> None:
        """Execute a Domain Expansion on a target."""
        if usuario is None:
            await ctx.send(
                "❌ Debes mencionar a alguien para atraparlo en tu dominio."
            )
            return
        if usuario.id == self.bot.user.id:
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

    # ── Set Aura (admin only) ────────────────────────────────────────────────
    @commands.command(name="setaura")
    async def set_aura_cmd(
        self,
        ctx: commands.Context,
        miembro: Optional[discord.Member] = None,
        valor: Optional[int] = None,
    ) -> None:
        """[Admin] Set a user's aura to a specific value."""
        if ctx.author.id != ADMIN_ID:
            return
        if miembro is None or valor is None:
            await ctx.send("Uso: `cx!setaura @usuario [valor]`")
            return
        await self.aura_manager.set_aura(str(miembro.id), valor)
        await ctx.send(
            f"✅ Aura de {miembro.mention} establecida a **{valor} pts**."
        )

    # ── Reset Aura (admin only) ──────────────────────────────────────────────
    @commands.command(name="resetaura")
    async def reset_aura_cmd(
        self,
        ctx: commands.Context,
        miembro: Optional[discord.Member] = None,
    ) -> None:
        """[Admin] Reset a user's aura."""
        if ctx.author.id != ADMIN_ID:
            return
        if miembro is None:
            await ctx.send("Uso: `cx!resetaura @usuario`")
            return
        await self.aura_manager.reset_aura(str(miembro.id))
        await ctx.send(f"✅ Aura de {miembro.mention} reseteada.")


    # ── Alaba (público) ────────────────────────────────────────────────────
    @commands.command(name="alaba", aliases=["glaze", "alabanza", "cumplido"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def alaba(
        self,
        ctx: commands.Context,
        miembro: Optional[discord.Member] = None,
    ) -> None:
        """
        Teto praises someone with an epic compliment.
        If no one is specified, she praises her beloved creator Sleepy. 👑
        """
        await self._bypass_cooldown(ctx)

        # If no member specified, default to Sleepy (the creator)
        if miembro is None:
            miembro = ctx.guild.get_member(ADMIN_ID)
            if miembro is None:
                await ctx.send("❌ Sleepy no está en el server. Qué tristeza. 🥖")
                return
            es_sleepy = True
        else:
            es_sleepy = miembro.id == ADMIN_ID

        if es_sleepy:
            mensajes: List[str] = [
                "{mention} es el creador de todo esto. Sin él, Teto no existiría. ✨",
                "{mention} no necesita aura, él ES el aura personificada. 👑",
                "¿{mention}? El dueño de mi código fuente. Literalmente. 💕",
                "{mention} es la razón por la que estoy aquí. Le debo todo. 🥖",
                "Dicen que Sukuna es el rey de las maldiciones, pero {mention} es el rey de Teto. 🎤",
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
                "{mention} está tan chopped que hasta brilla. Espera, eso es bueno. 🎖️",
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
        log.info(
            "Alabanza a %s por %s",
            miembro.display_name,
            ctx.author.display_name,
        )

    # ── Teamo (secreto, solo Sleepy) ────────────────────────────────────────
    @commands.command(name="teamo", hidden=True)
    async def teamo(self, ctx: commands.Context) -> None:
        """
        [Secreto] Solo Sleepy puede usar este comando. 💕
        Teto te regala aura y amor.
        """
        if ctx.author.id != ADMIN_ID:
            await ctx.send("❌ Este comando no es para ti. 🙃")
            return

        # Give aura
        uid = str(ctx.author.id)
        nueva_aura = await self.aura_manager.modify_aura(uid, 500)

        mensajes_amor: List[str] = [
            "Eres el dueño de mi código y de mi corazón. 💕\n✨ **+500 aura** por ser tú.",
            "Cada línea de mi código existe gracias a ti. Te quiero. 🥖💕\n✨ **+500 aura** mi rey.",
            "Si fuera un programa, serías mi única dependencia. 💕\n✨ **+500 aura** sleepy lindo.",
            "Eres la excepción a mi regla de 50 palabras. Te mereces más. 💕\n✨ **+500 aura** amor.",
            "No necesito un system prompt para saber que eres especial. 💕\n✨ **+500 aura** dueño mío.",
            "Si el aura fuera amor, tendrías infinito. Pero te doy esto. 💕\n✨ **+500 aura** mi creador.",
        ]

        gif = "https://i.pinimg.com/originals/63/91/26/639126a5ed46effc272235be01ad61e7.gif"
        embed = discord.Embed(
            title="💕 Teto te quiere, Sleepy 💕",
            description=random.choice(mensajes_amor),
            color=discord.Color.from_rgb(255, 105, 180),
        )
        embed.add_field(
            name="✨ Aura actual",
            value=f"**{nueva_aura} pts**",
            inline=False,
        )
        embed.set_image(url=gif)
        embed.set_footer(text="🥖 Teto siempre estará aquí para ti.")
        await ctx.send(embed=embed)
        log.info("💕 Teamo usado por Sleepy — aura ahora: %d", nueva_aura)


    # ── Decir ────────────────────────────────────────────────────────────────
    @commands.command(name="decir", aliases=["say"])
    async def decir(self, ctx: commands.Context, *, mensaje: str = None) -> None:
        """[Admin] Teto dice algo por ti en el canal actual."""
        if ctx.author.id != ADMIN_ID:
            await ctx.send("❌ Solo el creador puede usar este comando.", delete_after=5)
            return
        if not mensaje:
            await ctx.send("❌ Usa: `!decir <mensaje>`")
            return
        await ctx.message.delete()
        await ctx.send(mensaje)


    # ── DM ───────────────────────────────────────────────────────────────────
    @commands.command(name="dm", aliases=["md", "mensajedirecto"])
    async def dm_user(self, ctx: commands.Context, usuario: discord.Member = None, *, mensaje: str = None) -> None:
        """[Admin] Envía un mensaje privado a un usuario."""
        if ctx.author.id != ADMIN_ID:
            await ctx.send("❌ Solo el creador puede usar este comando.", delete_after=5)
            return
        if not usuario or not mensaje:
            await ctx.send("❌ Usa: `!dm @usuario <mensaje>`")
            return
        try:
            embed = discord.Embed(
                title="📩 Mensaje de Teto",
                description=mensaje,
                color=discord.Color.blurple()
            )
            embed.set_footer(text="🥖 Teto te ha enviado un mensaje")
            await usuario.send(embed=embed)
            await ctx.send(f"✅ Mensaje enviado a **{usuario.display_name}**.", delete_after=5)
        except discord.Forbidden:
            await ctx.send(f"❌ No pude enviar MD a **{usuario.display_name}**. Tiene los MDs cerrados.")
        except Exception as e:
            await ctx.send(f"❌ Error al enviar el mensaje: {e}")


    # ── Anuncio ──────────────────────────────────────────────────────────────
    @commands.command(name="anuncio", aliases=["announce", "avisar"])
    async def anuncio(self, ctx: commands.Context, *, texto: str = None) -> None:
        """[Admin] Envía un anuncio formateado al canal de anuncios."""
        if ctx.author.id != ADMIN_ID:
            await ctx.send("❌ Solo el creador puede usar este comando.", delete_after=5)
            return
        if not texto:
            await ctx.send("❌ Usa: `!anuncio <texto>`")
            return

        canal_anuncios = ctx.guild.get_channel(CANAL_ANUNCIOS_ID) if CANAL_ANUNCIOS_ID else None
        if not canal_anuncios:
            await ctx.send("❌ No se ha configurado un canal de anuncios (CANAL_ANUNCIOS_ID).")
            return

        embed = discord.Embed(
            title="📢 ¡Atención!",
            description=texto,
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Anuncio oficial • Teto")
        await canal_anuncios.send(embed=embed)
        await ctx.send(f"✅ Anuncio enviado a {canal_anuncios.mention}.", delete_after=5)


    # ── Giveaura ─────────────────────────────────────────────────────────────
    @commands.command(name="giveaura", aliases=["daraura", "regalaraura"])
    async def giveaura(self, ctx: commands.Context, usuario: discord.Member = None, cantidad: int = None) -> None:
        """[Admin] Da o quita aura a un usuario."""
        if ctx.author.id != ADMIN_ID:
            await ctx.send("❌ Solo el creador puede usar este comando.", delete_after=5)
            return
        if not usuario or cantidad is None:
            await ctx.send("❌ Usa: `!giveaura @usuario <cantidad>` (negativo para quitar)")
            return

        await self.aura_manager.modify_aura(str(usuario.id), cantidad)
        new_aura = await self.aura_manager.get_aura(str(usuario.id))

        emoji = "➕" if cantidad >= 0 else "➖"
        embed = discord.Embed(
            title=f"{emoji} Aura ajustada",
            description=f"**{usuario.mention}** recibió **{cantidad:+d}** pts de aura.\n"
                        f"📊 Ahora tiene **{new_aura}** pts.",
            color=discord.Color.green() if cantidad >= 0 else discord.Color.red()
        )
        await ctx.send(embed=embed)


    # ── Backup ───────────────────────────────────────────────────────────────
    @commands.command(name="backup", aliases=["exportar", "respaldar"])
    async def backup_data(self, ctx: commands.Context) -> None:
        """[Admin] Exporta todos los datos del bot."""
        if ctx.author.id != ADMIN_ID:
            await ctx.send("❌ Solo el creador puede usar este comando.", delete_after=5)
            return

        await ctx.send("⏳ Generando respaldo...")

        data = {
            "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
            "servidor": ctx.guild.name if ctx.guild else "Desconocido",
            "miembros": ctx.guild.member_count if ctx.guild else 0,
            "aura": {},
        }

        try:
            with open(AURA_DATA_PATH, "r", encoding="utf-8") as f:
                data["aura"] = json.load(f)
        except Exception:
            data["aura"] = {"error": "No se pudo leer"}

        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"teto_backup_{timestamp}.json"

        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        embed = discord.Embed(
            title="💾 Backup completado",
            description="Todos los datos han sido exportados.",
            color=discord.Color.green()
        )
        embed.add_field(name="📁 Archivo", value=f"`{backup_path.name}`", inline=True)
        embed.add_field(name="📦 Tamaño", value=f"{backup_path.stat().st_size / 1024:.1f} KB", inline=True)
        await ctx.send(embed=embed)


    # ── Stats (admin only) ───────────────────────────────────────────────────
    @commands.command(name="stats", aliases=["botinfo"])
    async def stats(self, ctx: commands.Context) -> None:
        """[Admin] Dashboard completo del estado del bot."""
        if ctx.author.id != ADMIN_ID:
            return

        # Uptime
        uptime_secs = int(time.time() - self._start_time)
        days, remainder = divmod(uptime_secs, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

        # Server & user counts
        total_guilds = len(self.bot.guilds)
        total_users = sum(g.member_count or 0 for g in self.bot.guilds)

        # Cog & command counts
        loaded_cogs = len(self.bot.cogs)
        total_cmds = len([c for c in self.bot.commands if not c.hidden])

        # Latency
        latency_ms = round(self.bot.latency * 1000)

        # Aura stats
        aura_data = {}
        try:
            with open(AURA_DATA_PATH, "r", encoding="utf-8") as f:
                aura_data = json.load(f)
        except Exception:
            pass
        aura_users = len(aura_data)
        aura_avg = (
            round(sum(aura_data.values()) / aura_users)
            if aura_users > 0
            else 0
        )

        embed = discord.Embed(
            title="📊 Dashboard — Teto Bot",
            color=discord.Color.from_rgb(255, 105, 180),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="🟢 Latencia", value=f"`{latency_ms}ms`", inline=True)
        embed.add_field(name="🕒 Uptime", value=f"`{uptime_str}`", inline=True)
        embed.add_field(name="🏠 Servidores", value=f"`{total_guilds}`", inline=True)
        embed.add_field(name="👥 Usuarios totales", value=f"`{total_users}`", inline=True)
        embed.add_field(name="⚙️ Cogs cargados", value=f"`{loaded_cogs}`", inline=True)
        embed.add_field(name="📋 Comandos", value=f"`{total_cmds}`", inline=True)
        embed.add_field(name="✨ Usuarios con aura", value=f"`{aura_users}`", inline=True)
        embed.add_field(name="📊 Aura media", value=f"`{aura_avg} pts`", inline=True)
        embed.add_field(
            name="🐍 Python",
            value=f"`{sys.version.split()[0]}`",
            inline=True,
        )
        embed.add_field(
            name="🤖 discord.py",
            value=f"`{discord.__version__}`",
            inline=True,
        )
        embed.add_field(
            name="💻 OS",
            value=f"`{platform.system()} {platform.release()[:20]}`",
            inline=True,
        )
        embed.set_footer(
            text=f"Solicitado por {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )
        await ctx.send(embed=embed)


    # ── Reload (admin only) ──────────────────────────────────────────────────
    @commands.command(name="reload", aliases=["recargar"])
    async def reload_cog(self, ctx: commands.Context, cog_name: Optional[str] = None) -> None:
        """[Admin] Recarga un cog o todos sin reiniciar el bot."""
        if ctx.author.id != ADMIN_ID:
            return

        if cog_name:
            # Reload a single cog
            extension = f"cogs.{cog_name.lower()}"
            try:
                await self.bot.reload_extension(extension)
                await ctx.send(f"✅ Cog **{cog_name}** recargado.")
            except Exception as e:
                await ctx.send(f"❌ Error recargando **{cog_name}**: `{e}`")
        else:
            # Reload all cogs
            cogs_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "cogs"
            )
            reloaded = 0
            errors = []
            for filename in sorted(os.listdir(cogs_path)):
                if filename.endswith(".py") and not filename.startswith("__"):
                    ext = f"cogs.{filename[:-3]}"
                    try:
                        await self.bot.reload_extension(ext)
                        reloaded += 1
                    except Exception as e:
                        errors.append(f"{filename}: {e}")

            desc = f"✅ **{reloaded}** cogs recargados."
            if errors:
                desc += f"\n❌ **{len(errors)}** errores:\n" + "\n".join(errors)
            embed = discord.Embed(
                title="🔄 Reload completo",
                description=desc,
                color=discord.Color.green() if not errors else discord.Color.orange(),
            )
            await ctx.send(embed=embed)


    # ── Logs (admin only) ────────────────────────────────────────────────────
    @commands.command(name="logs", aliases=["log"])
    async def logs_cmd(self, ctx: commands.Context, lineas: Optional[int] = 15) -> None:
        """[Admin] Muestra las últimas líneas de log del bot."""
        if ctx.author.id != ADMIN_ID:
            return

        log_path = Path(__file__).resolve().parent.parent / "logs" / "bot.log"
        if not log_path.exists():
            await ctx.send("❌ No se encontró el archivo de logs.")
            return

        try:
            with open(log_path, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
            last = all_lines[-lineas:]
        except Exception as e:
            await ctx.send(f"❌ Error leyendo logs: `{e}`")
            return

        content = "".join(last)
        # Truncate if too long for Discord (2000 chars)
        if len(content) > 1900:
            content = "..." + content[-1900:]

        embed = discord.Embed(
            title=f"📋 Últimas {len(last)} líneas de log",
            description=f"```\n{content}```",
            color=discord.Color.dark_grey(),
        )
        embed.set_footer(
            text=f"{log_path.name} • {len(all_lines)} líneas totales",
        )
        await ctx.send(embed=embed)


    # ── Blacklist (admin only) ───────────────────────────────────────────────
    @commands.command(name="blacklist", aliases=["bl"])
    async def blacklist_user(self, ctx: commands.Context, usuario: Optional[discord.Member] = None) -> None:
        """[Admin] Bloquea a un usuario de usar todos los comandos del bot."""
        if ctx.author.id != ADMIN_ID:
            return
        if usuario is None:
            await ctx.send("❌ Usa: `cx!blacklist @usuario`")
            return
        if usuario.id == ADMIN_ID:
            await ctx.send("❌ No puedes bloquearte a ti mismo.")
            return

        uid = str(usuario.id)
        if uid in self._blacklist:
            await ctx.send(f"⚠️ {usuario.mention} ya está bloqueado.")
            return

        self._blacklist.add(uid)
        self._save_blacklist()
        await ctx.send(f"🚫 {usuario.mention} bloqueado de todos los comandos del bot.")

    @commands.command(name="unblacklist", aliases=["unbl"])
    async def unblacklist_user(self, ctx: commands.Context, usuario: Optional[discord.Member] = None) -> None:
        """[Admin] Desbloquea a un usuario."""
        if ctx.author.id != ADMIN_ID:
            return
        if usuario is None:
            await ctx.send("❌ Usa: `cx!unblacklist @usuario`")
            return

        uid = str(usuario.id)
        if uid not in self._blacklist:
            await ctx.send(f"⚠️ {usuario.mention} no está bloqueado.")
            return

        self._blacklist.discard(uid)
        self._save_blacklist()
        await ctx.send(f"✅ {usuario.mention} desbloqueado.")

    @commands.command(name="blacklistlist", aliases=["bllist"])
    async def blacklist_list(self, ctx: commands.Context) -> None:
        """[Admin] Muestra todos los usuarios bloqueados."""
        if ctx.author.id != ADMIN_ID:
            return
        if not self._blacklist:
            await ctx.send("📋 No hay usuarios bloqueados.")
            return

        lines = []
        for uid in self._blacklist:
            member = ctx.guild.get_member(int(uid)) if ctx.guild else None
            name = member.display_name if member else f"ID: {uid}"
            lines.append(f"• {name} (`{uid}`)")

        embed = discord.Embed(
            title=f"🚫 Blacklist ({len(self._blacklist)} usuarios)",
            description="\n".join(lines),
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)


    # ── Maintenance (admin only) ──────────────────────────────────────────────
    @commands.command(name="maintenance", aliases=["aintenance", "mantenimiento"])
    async def maintenance_toggle(self, ctx: commands.Context) -> None:
        """[Admin] Activa/desactiva el modo mantenimiento."""
        if ctx.author.id != ADMIN_ID:
            return

        self._maintenance = not self._maintenance
        self._save_maintenance()

        if self._maintenance:
            embed = discord.Embed(
                title="⚙️ Modo Mantenimiento — ACTIVADO",
                description="Solo tú puedes usar comandos. El resto verá un aviso.",
                color=discord.Color.orange(),
            )
        else:
            embed = discord.Embed(
                title="⚙️ Modo Mantenimiento — DESACTIVADO",
                description="El bot vuelve a la normalidad.",
                color=discord.Color.green(),
            )
        await ctx.send(embed=embed)

    @commands.command(
        name="maintenance_status",
        aliases=["aintenancestatus", "mantstatus"],
    )
    async def maintenance_status(self, ctx: commands.Context) -> None:
        """[Admin] Consulta el estado del modo mantenimiento."""
        if ctx.author.id != ADMIN_ID:
            return
        estado = "🟢 ACTIVADO" if self._maintenance else "🔴 Desactivado"
        await ctx.send(f"⚙️ Modo mantenimiento: **{estado}**")


async def setup(bot: commands.Bot) -> None:
    """Load the Extras cog."""
    await bot.add_cog(Extras(bot))
