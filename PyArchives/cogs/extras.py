"""
Extras cog — fun and interactive commands for the Teto Discord bot.
Includes the Aura system, GIF commands (Black Flash, Domain Expansion),
duels, robberies, voting, reminders, dice, and more.
"""
import asyncio
import json
import logging
import random
import time
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import discord
from discord.ext import commands, tasks

from config import ADMIN_ID, AURA_DATA_PATH, CANAL_ANUNCIOS_ID, VOTOS_CHOPPED_PATH
from utils.aura_manager import AuraManager
from utils.gif_manager import get_giphy_gif

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


def _cargar_votos(votos_path: Path) -> Dict[str, list]:
    """Load chopped votes from JSON file."""
    if not votos_path.exists():
        return {}
    try:
        with open(votos_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _guardar_votos(data: Dict[str, list], votos_path: Path) -> None:
    """Save chopped votes to JSON file atomically."""
    temp = votos_path.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp.replace(votos_path)


def _limpiar_votos_expirados(votos: Dict[str, list], ahora: float) -> None:
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
        self._votos_chopped: Dict[str, list] = _cargar_votos(VOTOS_CHOPPED_PATH)
        self.chopped_task.start()

    def cog_unload(self) -> None:
        """Clean up when the cog is unloaded."""
        self.chopped_task.cancel()

    # ── Admin Cooldown Bypass ────────────────────────────────────────────────
    async def _bypass_cooldown(self, ctx: commands.Context) -> None:
        """Remove cooldown for the configured admin."""
        if ctx.author.id == ADMIN_ID:
            ctx.command.reset_cooldown(ctx)

    # ── Chopped Task (every 6 hours) ─────────────────────────────────────────
    @tasks.loop(hours=6)
    async def chopped_task(self) -> None:
        """Pick a random member and publicly declare them chopped."""
        canal = self.bot.get_channel(CANAL_ANUNCIOS_ID)
        if canal is None:
            return
        guild = canal.guild
        humanos = [m for m in guild.members if not m.bot]
        if not humanos:
            return
        elegido = random.choice(humanos)
        mensaje = random.choice(MENSAJES_CHOPPED).format(mention=elegido.mention)
        await canal.send(mensaje)
        log.info("Chopped aleatorio: %s", elegido.display_name)

    @chopped_task.before_loop
    async def before_chopped(self) -> None:
        """Wait for the bot to be ready before starting the loop."""
        await self.bot.wait_until_ready()

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
        embed.set_image(url=self.aura_manager.get_aura_gif(puntos))
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

    # ── Duelo de Aura ────────────────────────────────────────────────────────
    @commands.command(name="da", aliases=["dueloaura"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def duelo_aura(
        self,
        ctx: commands.Context,
        rival: Optional[discord.Member] = None,
    ) -> None:
        """Aura duel. Winner gets +50, loser gets -100."""
        await self._bypass_cooldown(ctx)
        if rival is None:
            await ctx.send("❌ Menciona a tu rival.")
            return
        if rival.bot:
            await ctx.send("❌ El bot tiene inmunidad diplomática.")
            return
        if rival.id == ctx.author.id:
            await ctx.send("❌ No puedes duelarte contigo mismo.")
            return

        uid_autor = str(ctx.author.id)
        uid_rival = str(rival.id)

        # Randomly determine winner
        if random.random() < 0.5:
            ganador, perdedor = ctx.author, rival
            uid_gan, uid_per = uid_autor, uid_rival
        else:
            ganador, perdedor = rival, ctx.author
            uid_gan, uid_per = uid_rival, uid_autor

        aura_gan = await self.aura_manager.modify_aura(uid_gan, 50)
        aura_per = await self.aura_manager.modify_aura(uid_per, -100)

        razon = random.choice(RAZONES_VERSUS).format(
            perdedor=perdedor.display_name
        )

        embed = discord.Embed(
            title="⚔️ Duelo de Aura",
            color=discord.Color.gold(),
        )
        embed.add_field(
            name="🏆 Ganador",
            value=f"{ganador.mention} — **{aura_gan} pts** (+50)",
            inline=False,
        )
        embed.add_field(
            name="💀 Perdedor",
            value=f"{perdedor.mention} — **{aura_per} pts** (-100)",
            inline=False,
        )
        embed.add_field(
            name="📖 Lore",
            value=f"{ganador.mention} ganó {razon}",
            inline=False,
        )
        await ctx.send(embed=embed)

    # ── Robo de Aura ─────────────────────────────────────────────────────────
    @commands.command(name="robar", aliases=["rob"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def robar_aura(
        self,
        ctx: commands.Context,
        objetivo: Optional[discord.Member] = None,
    ) -> None:
        """Attempt to steal aura. 50% success rate. Failure costs you."""
        await self._bypass_cooldown(ctx)
        if objetivo is None:
            await ctx.send("❌ Menciona a quién quieres robar.")
            return
        if objetivo.bot:
            await ctx.send("❌ El bot no tiene aura robable.")
            return
        if objetivo.id == ctx.author.id:
            await ctx.send("❌ No puedes robarte a ti mismo.")
            return

        cantidad = random.randint(50, 300)
        uid_ladron = str(ctx.author.id)
        uid_obj = str(objetivo.id)

        if random.random() < 0.5:
            # Success
            await self.aura_manager.modify_aura(uid_ladron, cantidad)
            await self.aura_manager.modify_aura(uid_obj, -cantidad)
            await ctx.send(
                f"🥷 **ROBO EXITOSO.** {ctx.author.mention} le ha birlado "
                f"**{cantidad} pts** de aura a {objetivo.mention}. "
                "Sin dejar rastro."
            )
        else:
            # Failure — thief loses aura
            await self.aura_manager.modify_aura(uid_ladron, -cantidad)
            await ctx.send(
                f"💀 **PILLADO.** {ctx.author.mention} intentó robarle a "
                f"{objetivo.mention} y le salió mal. "
                f"Pierde **{cantidad} pts** de aura."
            )

    # ── Castigo (non-blocking) ───────────────────────────────────────────────
    @commands.command(name="castigo", aliases=["cast"])
    @commands.cooldown(1, 30, commands.BucketType.user)
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
                    asyncio.create_task(
                        self._delayed_edit(usuario, dur, mute=False)
                    )

            elif tipo == "deaf":
                if not usuario.voice:
                    await ctx.send("❌ Esa persona no está en un canal de voz.")
                    return
                await usuario.edit(deafen=True)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
                if dur:
                    asyncio.create_task(
                        self._delayed_edit(usuario, dur, deafen=False)
                    )

            elif tipo == "mute_deaf":
                if not usuario.voice:
                    await ctx.send("❌ Esa persona no está en un canal de voz.")
                    return
                await usuario.edit(mute=True, deafen=True)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
                if dur:
                    asyncio.create_task(
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

    # ── Dado ─────────────────────────────────────────────────────────────────
    @commands.command(name="dado", aliases=["dice", "d"])
    async def dado(self, ctx: commands.Context, caras: int = 6) -> None:
        """Roll a die. Usage: cx!dado [sides] — defaults to d6."""
        await self._bypass_cooldown(ctx)
        if caras < 2 or caras > 1000:
            await ctx.send("❌ El dado tiene que tener entre 2 y 1000 caras.")
            return
        resultado = random.randint(1, caras)
        await ctx.send(f"🎲 **d{caras}** → `{resultado}`")

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

        asyncio.create_task(_enviar_recordatorio())

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


async def setup(bot: commands.Bot) -> None:
    """Load the Extras cog."""
    await bot.add_cog(Extras(bot))
