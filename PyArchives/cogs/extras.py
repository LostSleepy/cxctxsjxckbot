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
from discord.ext import commands

from config import ADMIN_ID, AURA_DATA_PATH, BASE_DIR, CANAL_ANUNCIOS_ID, VOTOS_CHOPPED_PATH
from utils.aura_manager import AuraManager
from utils.gif_manager import get_aura_gif, get_giphy_gif

# ── Data files ────────────────────────────────────────────────────────────────
DEDOS_DATA_PATH: Path = BASE_DIR / "dedos_data.json"
INVENTARIO_PATH: Path = BASE_DIR / "inventario_data.json"
TIENDA_PATH: Path = BASE_DIR / "tienda_data.json"
EFECTOS_PATH: Path = BASE_DIR / "active_effects.json"

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


def _cargar_dedos(path: Path = DEDOS_DATA_PATH) -> Dict[str, int]:
    """Load finger data from JSON file."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _guardar_dedos(data: Dict[str, int], path: Path = DEDOS_DATA_PATH) -> None:
    """Save finger data to JSON file atomically."""
    temp = path.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp.replace(path)


def _cargar_inventario(path: Path = INVENTARIO_PATH) -> Dict[str, list]:
    """Load inventory data from JSON file."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _guardar_inventario(data: Dict[str, list], path: Path = INVENTARIO_PATH) -> None:
    """Save inventory data to JSON file atomically."""
    temp = path.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp.replace(path)


def _cargar_efectos(path: Path = EFECTOS_PATH) -> Dict[str, dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _guardar_efectos(data: Dict[str, dict], path: Path = EFECTOS_PATH) -> None:
    temp = path.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp.replace(path)


# ── Shop items ─────────────────────────────────────────────────────────────────
TIENDA_ITEMS: List[dict] = [
    {"id": "glow", "nombre": "✨ Brillo de Aura", "desc": "Tu nombre brilla en el ranking.", "precio": 500},
    {"id": "skip", "nombre": "🔄 Reintento de Aura", "desc": "Vuelve a tirar tu aura del día.", "precio": 800},
    {"id": "shield", "nombre": "🛡️ Escudo de Aura", "desc": "Te protege de 1 robo de aura.", "precio": 600},
    {"id": "boost", "nombre": "🚀 Multiplicador x2", "desc": "Tu próximo +aura se duplica.", "precio": 1200},
]


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
        self._dedos: Dict[str, int] = _cargar_dedos(DEDOS_DATA_PATH)
        self._inventario: Dict[str, list] = _cargar_inventario(INVENTARIO_PATH)
        self._tienda_items: List[dict] = TIENDA_ITEMS
        self._ahorcado_juegos: Dict[int, dict] = {}  # channel_id -> game state

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

        # Check for boost
        uid = str(miembro.id)
        efectos = _cargar_efectos()
        boost_activo = efectos.get(uid, {}).get("boost", False)
        if boost_activo and miembro.id == ctx.author.id:
            puntos *= 2
            efectos[uid]["boost"] = False
            _guardar_efectos(efectos)

        embed = discord.Embed(
            title=f"✨ Aura de {miembro.display_name}",
            description=self.aura_manager.get_aura_message(puntos),
            color=discord.Color.gold() if puntos >= 0 else discord.Color.dark_red(),
        )
        if boost_activo and miembro.id == ctx.author.id:
            embed.description += "\n\n🚀 **¡Boost activado!** Has recibido el doble de aura."
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
        inventario_data = _cargar_inventario()
        lineas: List[str] = []
        for i, (uid, puntos) in enumerate(ranking):
            nombre = ctx.guild.get_member(int(uid))
            display = nombre.display_name if nombre else f"ID:{uid}"
            # Check if user has the glow item
            tiene_glow = False
            if uid in inventario_data:
                tiene_glow = any(item["id"] == "glow" for item in inventario_data[uid].get("items", []))
            if tiene_glow:
                display = f"✨{display}✨"
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

        # Check if target has shield
        efectos = _cargar_efectos()
        escudos = efectos.get(uid_obj, {}).get("shields", 0)
        if escudos > 0:
            efectos[uid_obj]["shields"] = escudos - 1
            _guardar_efectos(efectos)
            await ctx.send(
                f"🛡️ **ESCUDO ACTIVADO.** {ctx.author.mention} intentó robar a "
                f"{objetivo.mention} pero su escudo lo protegió. "
                f"Le queda(n) **{escudos - 1}** escudo(s)."
            )
            return

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


    # ── PPT (Piedra, Papel, Tijera) ────────────────────────────────────────
    @commands.command(name="ppt", aliases=["piedrapapeltijera", "piedra"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ppt(self, ctx: commands.Context, *, eleccion: str = None) -> None:
        """Juega piedra, papel o tijera contra Teto."""
        await self._bypass_cooldown(ctx)
        opciones = {"piedra": "🪨", "papel": "📄", "tijera": "✂️"}
        if eleccion is None or eleccion.lower() not in opciones:
            await ctx.send("❌ Elige: `piedra`, `papel` o `tijera`. Ej: `cx!ppt piedra`")
            return

        user_choice = eleccion.lower()
        bot_choice = random.choice(list(opciones.keys()))
        reglas = {"piedra": "tijera", "tijera": "papel", "papel": "piedra"}

        if user_choice == bot_choice:
            resultado = "🤝 **Empate**"
        elif reglas[user_choice] == bot_choice:
            resultado = "🎉 **Ganaste**"
            win_aura = random.randint(10, 50)
            await self.aura_manager.modify_aura(str(ctx.author.id), win_aura)
            resultado += f" ¡+{win_aura} aura!"
        else:
            resultado = "💀 **Perdiste**"

        await ctx.send(
            f"{opciones[user_choice]} Tú → {opciones[bot_choice]} Teto\n"
            f"{resultado}"
        )

    # ── Coinflip ──────────────────────────────────────────────────────────────
    @commands.command(name="coinflip", aliases=["tirar", "caraocruz"])
    async def coinflip(self, ctx: commands.Context) -> None:
        """Lanza una moneda al aire."""
        resultado = random.choice(["🇨 **Cara**", "🇽 **Cruz**"])
        await ctx.send(f"🪙 La moneda dice... {resultado}")

    # ── Insultar ──────────────────────────────────────────────────────────────
    @commands.command(name="insultar", aliases=["insulto"])
    async def insultar(self, ctx: commands.Context, objetivo: discord.Member = None) -> None:
        """Insulta a alguien con ingenio."""
        if objetivo is None:
            await ctx.send("❌ Menciona a alguien para insultar.")
            return
        if objetivo.bot:
            await ctx.send("❌ Al bot no se le insulta. El bot os insulta a vosotros.")
            return
        if objetivo.id == ctx.author.id:
            await ctx.send("❌ No te puedes insultar a ti mismo... bueno, puedes, pero qué triste.")
            return

        insultos = [
            f"{objetivo.mention} tiene menos aura que una piedra. 🪨",
            f"{objetivo.mention} es tan chopped que las plantas a su lado piden agua. 🌱",
            f"{objetivo.mention} confundió una API con un refresco. 🥤",
            f"{objetivo.mention} tiene el CI de una maceta. Y la maceta riega sola. 🪴",
            f"{objetivo.mention} perdió contra un bot en piedra, papel o tijera. 🤡",
            f"{objetivo.mention} usa Internet Explorer en Discord. 🐢",
            f"{objetivo.mention} tiene menos dedos de Sukuna que Yuji al empezar. 0. 🥖",
            f"{objetivo.mention} es la razón por la que pusieron tutoriales en los videojuegos. 📖",
        ]
        await ctx.send(random.choice(insultos))

    # ── Felicitar ─────────────────────────────────────────────────────────────
    @commands.command(name="felicitar", aliases=["feli", "felicitacion"])
    async def felicitar(self, ctx: commands.Context, objetivo: discord.Member = None) -> None:
        """Felicita a alguien con cariño."""
        if objetivo is None:
            objetivo = ctx.author

        felicitaciones = [
            f"{objetivo.mention} es tan guay que hasta Sukuna aplaudiría. 👏",
            f"{objetivo.mention} tiene más brillo que un Black Flash. ⚡",
            f"{objetivo.mention} es la definición de main character. 🎬",
            f"{objetivo.mention} hoy está imparable. Y eso mola. 🚀",
            f"{objetivo.mention} tiene más aura que todo el server junto. 🔥",
            f"{objetivo.mention} simplemente lo petas, no hay más. 🏆",
            f"{objetivo.mention} es el prota de esta temporada. 📺",
            f"Si {objetivo.mention} fuera un hechicero, sería de grado especial. 🎌",
        ]
        await ctx.send(f"🌟 {random.choice(felicitaciones)}")

    # ── Maldición ─────────────────────────────────────────────────────────────
    @commands.command(name="maldicion", aliases=["mal", "maldice"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def maldicion(self, ctx: commands.Context, objetivo: discord.Member = None) -> None:
        """Lanza una maldición temática de Jujutsu Kaisen."""
        await self._bypass_cooldown(ctx)
        if objetivo is None:
            await ctx.send("❌ Menciona a alguien para maldecir.")
            return
        if objetivo.bot:
            await ctx.send("❌ El bot es inmune a las maldiciones.")
            return
        if objetivo.id == ctx.author.id:
            await ctx.send("❌ No te puedes maldecir a ti mismo... creo.")
            return

        maldiciones = [
            f"{objetivo.mention} ha sido maldecido con energía maldita de nivel especial. 💀",
            f"{objetivo.mention} ha caído bajo la **Expansión de Dominio** de {ctx.author.mention}. 🏮",
            f"{objetivo.mention} ahora tiene una maldición de grado 1. Que se lo piense. 🎌",
            f"{objetivo.mention} ha sido marcado por Sukuna. No hay escapatoria. 👹",
            f"{objetivo.mention} ha recibido una maldición tan fuerte que hasta Mahito se asustaría. 😈",
            f"La energía maldita de {ctx.author.mention} envuelve a {objetivo.mention}. **RIP**. ⚰️",
            f"{objetivo.mention} acaba de ser maldecido. Su aura disminuye por el miedo. 📉",
        ]

        # Small aura penalty
        perdida = random.randint(10, 30)
        await self.aura_manager.modify_aura(str(objetivo.id), -perdida)

        embed = discord.Embed(
            title="👹 MALDICIÓN",
            description=random.choice(maldiciones),
            color=discord.Color.dark_purple(),
        )
        embed.add_field(name="💫 Aura perdida", value=f"**-{perdida} pts**", inline=True)
        await ctx.send(embed=embed)


    # ── Ritual ──────────────────────────────────────────────────────────────
    @commands.command(name="ritual", aliases=["invocacion", "invocar"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ritual(self, ctx: commands.Context) -> None:
        """Teto realiza un ritual misterioso con efectos aleatorios en tu aura."""
        await self._bypass_cooldown(ctx)
        await ctx.trigger_typing()
        await asyncio.sleep(1)

        efectos = [
            ("🔥 **Ritual de Fuego**", random.randint(30, 80), "El espíritu del fuego te bendice con aura."),
            ("🌊 **Ritual de Agua**", random.randint(20, 50), "Las aguas de la purificación fortalecen tu alma."),
            ("🌪️ **Ritual de Viento**", random.randint(10, 40), "El viento susurra secretos que aumentan tu poder."),
            ("🌍 **Ritual de Tierra**", random.randint(5, 30), "La tierra firme te da estabilidad y aura."),
            ("💀 **Ritual de Maldición**", random.randint(-50, -10), "Algo salió mal... el ritual se volvió en tu contra."),
            ("✨ **Ritual de Estrellas**", random.randint(40, 100), "Las estrellas se alinean a tu favor. ¡Aura masiva!"),
            ("👻 **Ritual Vacío**", 0, "El ritual no tuvo efecto... o eso crees."),
            ("🎭 **Ritual de la Dualidad**", random.choice([-30, 30]), "El equilibrio del universo se manifiesta."),
            ("🏆 **Gran Ritual de Sukuna**", random.randint(50, 150), "¡Sukuna ha notado tu presencia! El aura fluye hacia ti."),
            ("💔 **Ritual Quebrado**", random.randint(-80, -20), "El ritual se rompió. Has perdido aura en el proceso."),
        ]

        nombre, cantidad, desc = random.choice(efectos)
        await self.aura_manager.modify_aura(str(ctx.author.id), cantidad)

        embed = discord.Embed(
            title="🔮 Ritual de Teto",
            description=f"{ctx.author.mention} ha realizado un ritual...\n\n**{nombre}**\n{desc}",
            color=discord.Color.dark_purple()
        )
        if cantidad >= 0:
            embed.add_field(name="✨ Aura obtenida", value=f"**+{cantidad} pts**", inline=True)
        else:
            embed.add_field(name="💫 Aura perdida", value=f"**{cantidad} pts**", inline=True)
        embed.set_footer(text="🥖 Los espíritus han hablado.")
        await ctx.send(embed=embed)


    # ── Dedo (de Sukuna) ─────────────────────────────────────────────────────
    @commands.command(name="dedo", aliases=["dedosukuna", "buscardedo"])
    @commands.cooldown(1, 600, commands.BucketType.user)  # 10 min cooldown
    async def dedo(self, ctx: commands.Context) -> None:
        """Busca un dedo de Sukuna. ¡Colecciónalos todos!"""
        await self._bypass_cooldown(ctx)

        # Load current dedos data
        dedos = _cargar_dedos()
        uid = str(ctx.author.id)
        user_dedos = dedos.get(uid, {"nombre": ctx.author.name, "cantidad": 0})

        # 30% chance to find a finger
        if random.random() < 0.3:
            user_dedos["cantidad"] += 1
            dedos[uid] = user_dedos
            _guardar_dedos(dedos)

            total = user_dedos["cantidad"]
            embed = discord.Embed(
                title="👆 ¡Has encontrado un dedo de Sukuna!",
                description=f"{ctx.author.mention} ha encontrado un dedo maldito.\n"
                            f"Ahora tienes **{total}** dedo{'s' if total != 1 else ''}.",
                color=discord.Color.dark_red()
            )

            # A small aura bonus for finding a finger
            bonus = random.randint(5, 15)
            await self.aura_manager.modify_aura(str(ctx.author.id), bonus)
            embed.add_field(name="✨ Bonus de aura", value=f"+{bonus} pts por tu hallazgo", inline=False)

            if total >= 20:
                embed.set_footer(text="👑 ¡Estás más cerca de convertirte en el recipiente de Sukuna!")
            else:
                embed.set_footer(text=f"💀 Te faltan {20 - total} dedos para el poder absoluto.")
        else:
            embed = discord.Embed(
                title="😔 No hubo suerte",
                description=f"{ctx.author.mention} buscó pero no encontró ningún dedo de Sukuna...\n"
                            f"¡Sigue intentándolo!",
                color=discord.Color.dark_grey()
            )
            embed.set_footer(text="🦊 Los dedos de Sukuna son difíciles de encontrar.")

        await ctx.send(embed=embed)


    # ── Sukuna (progreso) ────────────────────────────────────────────────────
    @commands.command(name="sukuna", aliases=["dedos", "misdedos"])
    async def sukuna_info(self, ctx: commands.Context) -> None:
        """Muestra cuántos dedos de Sukuna has recolectado."""
        dedos = _cargar_dedos()
        uid = str(ctx.author.id)
        user_dedos = dedos.get(uid, {"nombre": ctx.author.name, "cantidad": 0})
        cantidad = user_dedos["cantidad"]

        # Calculate progress bar
        max_dedos = 20
        progreso = min(cantidad, max_dedos)
        barra = "🟥" * progreso + "⬛" * (max_dedos - progreso)

        embed = discord.Embed(
            title="👆 Dedos de Sukuna",
            description=f"{ctx.author.mention}, has recolectado:",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="📊 Progreso", value=f"**{cantidad}** / **{max_dedos}** dedos\n{barra}", inline=False)

        if cantidad == 0:
            embed.add_field(name="💭", value="Aún no has encontrado ningún dedo. ¡Usa `dedo` para buscar!", inline=False)
        elif cantidad < 5:
            embed.add_field(name="🌱", value="Apenas estás comenzando tu viaje. Sigue buscando.", inline=False)
        elif cantidad < 10:
            embed.add_field(name="🔥", value="Vas tomando fuerza. Sukuna empieza a notarte.", inline=False)
        elif cantidad < 15:
            embed.add_field(name="⚡", value="Eres un recolector serio. El poder fluye en ti.", inline=False)
        elif cantidad < 20:
            embed.add_field(name="👑", value="¡Estás muy cerca del poder absoluto!", inline=False)
        else:
            embed.add_field(name="💀 ¡ERES EL RECIPIENTE!", value="¡Has alcanzado el poder máximo de Sukuna!", inline=False)

        # Top 3 dedos
        sorted_users = sorted(dedos.items(), key=lambda x: x[1]["cantidad"], reverse=True)[:3]
        if sorted_users:
            top_text = ""
            for i, (uid_data, info) in enumerate(sorted_users, 1):
                medal = ["🥇", "🥈", "🥉"][i - 1]
                top_text += f"{medal} **{info['nombre']}** — {info['cantidad']} dedos\n"
            embed.add_field(name="🏆 Top Recolectores", value=top_text, inline=False)

        await ctx.send(embed=embed)


    # ── Tienda ───────────────────────────────────────────────────────────────
    @commands.command(name="tienda", aliases=["shop", "mercadillo"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tienda(self, ctx: commands.Context) -> None:
        """Muestra los objetos disponibles para comprar con aura."""
        await self._bypass_cooldown(ctx)

        embed = discord.Embed(
            title="🛒 Tienda de Teto",
            description="Compra objetos con tu aura usando `!comprar <código>`",
            color=discord.Color.gold()
        )

        for item in TIENDA_ITEMS:
            emoji = item.get("emoji", "📦")
            embed.add_field(
                name=f"{emoji} **{item['nombre']}** — `{item['id']}`",
                value=f"💰 **{item['precio']}** aura — {item['desc']}",
                inline=False
            )

        embed.set_footer(text="🥖 ¡Gasta con moderación!")
        await ctx.send(embed=embed)


    # ── Comprar ───────────────────────────────────────────────────────────────
    @commands.command(name="comprar", aliases=["buy", "adquirir"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def comprar(self, ctx: commands.Context, *, item_id: str = None) -> None:
        """Compra un objeto de la tienda con tu aura."""
        await self._bypass_cooldown(ctx)

        if not item_id:
            await ctx.send("❌ Usa: `!comprar <código>`. Mira `!tienda` para ver los códigos.")
            return

        item_id = item_id.strip().lower()
        item = next((i for i in TIENDA_ITEMS if i["id"] == item_id), None)

        if not item:
            await ctx.send(f"❌ El objeto `{item_id}` no existe. Usa `!tienda` para ver los disponibles.")
            return

        # Check if user has enough aura
        aura_actual = await self.aura_manager.get_aura(str(ctx.author.id))
        precio = item["precio"]

        if aura_actual < precio:
            falta = precio - aura_actual
            await ctx.send(f"❌ No tienes suficiente aura. Te faltan **{falta} pts** para comprar **{item['nombre']}**.")
            return

        # Deduct aura
        await self.aura_manager.modify_aura(str(ctx.author.id), -precio)

        # Add to inventory
        inventario = _cargar_inventario()
        uid = str(ctx.author.id)
        if uid not in inventario:
            inventario[uid] = {"nombre": ctx.author.name, "items": []}
        inventario[uid]["items"].append({
            "id": item["id"],
            "nombre": item["nombre"],
            "fecha": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        _guardar_inventario(inventario)

        embed = discord.Embed(
            title="✅ ¡Compra realizada!",
            description=f"{ctx.author.mention} ha comprado **{item['nombre']}** por **{precio} aura**.\n"
                        f"💰 Te quedan **{aura_actual - precio}** pts de aura.",
            color=discord.Color.green()
        )
        embed.set_footer(text="🥖 ¡Disfruta de tu objeto!")
        await ctx.send(embed=embed)


    # ── Inventario ────────────────────────────────────────────────────────────
    @commands.command(name="inventario", aliases=["inv", "bolsillo"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def inventario(self, ctx: commands.Context) -> None:
        """Muestra los objetos que has comprado en la tienda."""
        await self._bypass_cooldown(ctx)

        inventario = _cargar_inventario()
        uid = str(ctx.author.id)
        user_inv = inventario.get(uid)

        if not user_inv or not user_inv["items"]:
            embed = discord.Embed(
                title="🎒 Inventario vacío",
                description=f"{ctx.author.mention} aún no tiene objetos.\n"
                            f"Usa `!tienda` para ver qué puedes comprar.",
                color=discord.Color.dark_grey()
            )
            await ctx.send(embed=embed)
            return
        
        # Count items by type
        item_counts = {}
        for item in user_inv["items"]:
            name = item["nombre"]
            item_counts[name] = item_counts.get(name, 0) + 1

        embed = discord.Embed(
            title=f"🎒 Inventario de {ctx.author.display_name}",
            description=f"Tienes **{len(user_inv['items'])}** objeto{'s' if len(user_inv['items']) != 1 else ''}:",
            color=discord.Color.blue()
        )

        items_text = ""
        for name, count in item_counts.items():
            items_text += f"• **{name}** x{count}\n"
        embed.add_field(name="📦 Objetos", value=items_text, inline=False)

        # Show last 5 purchases
        last_items = user_inv["items"][-5:]
        last_items.reverse()
        recent = "\n".join([f"• {i['nombre']} — {i.get('fecha', 'desconocida')}" for i in last_items])
        embed.add_field(name="🕐 Últimas adquisiciones", value=recent, inline=False)

        aura = await self.aura_manager.get_aura(str(ctx.author.id))
        embed.set_footer(text=f"🥖 Aura: {aura} pts | Sigue coleccionando")
        await ctx.send(embed=embed)

    # ── Usar objetos ────────────────────────────────────────────────────────────
    @commands.command(name="usar")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def usar_item(self, ctx: commands.Context, *, item_id: str = None) -> None:
        """Usa un objeto de tu inventario: glow, skip, shield, boost"""
        await self._bypass_cooldown(ctx)

        VALID_ITEMS = {
            "skip": "🔄 Reintento de Aura",
            "shield": "🛡️ Escudo de Aura",
            "boost": "🚀 Multiplicador x2",
        }

        if not item_id or item_id not in VALID_ITEMS:
            await ctx.send(
                f"❌ Usa: `!usar <item>`\nItems disponibles: {', '.join(f'`{k}`' for k in VALID_ITEMS)}"
            )
            return

        uid = str(ctx.author.id)

        # Load inventory
        inventario = _cargar_inventario()
        user_items = inventario.get(uid, [])

        # Check if user has the item
        idx = None
        for i, item in enumerate(user_items):
            if item["id"] == item_id:
                idx = i
                break

        if idx is None:
            await ctx.send(f"❌ No tienes **{VALID_ITEMS[item_id]}** en tu inventario.")
            return

        # Remove the item from inventory
        user_items.pop(idx)
        inventario[uid] = user_items
        _guardar_inventario(inventario)

        item_nombre = VALID_ITEMS[item_id]

        # Apply effects
        if item_id == "skip":
            # Remove user's aura data so get_aura generates a new value
            await self.aura_manager.reset_aura(uid)
            # But this would need them to use !aura to see it
            await ctx.send(
                f"🔄 **Reintento de Aura** activado. Usa `!aura` para obtener "
                "una nueva aura diaria."
            )

        elif item_id == "shield":
            efectos = _cargar_efectos()
            if uid not in efectos:
                efectos[uid] = {}
            efectos[uid]["shields"] = efectos[uid].get("shields", 0) + 1
            _guardar_efectos(efectos)
            escudos_totales = efectos[uid]["shields"]
            await ctx.send(
                f"🛡️ **Escudo de Aura** activado. Tienes **{escudos_totales}** "
                f"escudo{'s' if escudos_totales != 1 else ''} activo{'s' if escudos_totales != 1 else ''}. "
                "El próximo robo que reciban será bloqueado."
            )

        elif item_id == "boost":
            efectos = _cargar_efectos()
            if uid not in efectos:
                efectos[uid] = {}
            efectos[uid]["boost"] = True
            _guardar_efectos(efectos)
            await ctx.send(
                f"🚀 **Multiplicador x2** activado. Tu próximo `!aura` te dará "
                "el doble de puntos."
            )

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


    # ── Say (canal específico) ───────────────────────────────────────────────
    @commands.command(name="saycanal", aliases=["hablar", "deciren"])
    async def say_canal(self, ctx: commands.Context, canal: discord.TextChannel = None, *, mensaje: str = None) -> None:
        """[Admin] Teto habla en un canal específico."""
        if ctx.author.id != ADMIN_ID:
            await ctx.send("❌ Solo el creador puede usar este comando.", delete_after=5)
            return
        if not canal or not mensaje:
            await ctx.send("❌ Usa: `!saycanal #canal <mensaje>`")
            return
        try:
            await canal.send(mensaje)
            await ctx.send(f"✅ Mensaje enviado a {canal.mention}.", delete_after=5)
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")


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
            "dedos": {},
            "inventario": {},
        }

        try:
            with open(AURA_DATA_PATH, "r", encoding="utf-8") as f:
                data["aura"] = json.load(f)
        except:
            data["aura"] = {"error": "No se pudo leer"}

        dedos = _cargar_dedos()
        data["dedos"] = dedos

        inv = _cargar_inventario()
        data["inventario"] = inv

        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"teto_backup_{timestamp}.json"

        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        embed = discord.Embed(
            title="💾 Backup completado",
            description=f"Todos los datos han sido exportados.",
            color=discord.Color.green()
        )
        embed.add_field(name="📁 Archivo", value=f"`{backup_path.name}`", inline=True)
        embed.add_field(name="📦 Tamaño", value=f"{backup_path.stat().st_size / 1024:.1f} KB", inline=True)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Load the Extras cog."""
    await bot.add_cog(Extras(bot))
