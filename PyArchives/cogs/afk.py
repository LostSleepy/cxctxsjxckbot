"""
AFK Detection cog — Teto Discord Bot
--------------------------------------
Detects AFK farmers in voice channels, verifies via DM, kicks if no response.
Features:
  - JSON persistence (survives bot restarts)
  - Strike system (weekly + all-time leaderboard)
  - Weekly top publication (Sundays 00:00 Spain)
  - Configurable per-guild: timeout, excluded channels, whitelisted roles
  - Centralized management: cx!afkgest <subcommand>
"""
import json
import logging
import random
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import discord
import pytz
from discord.ext import commands, tasks

from config import ADMIN_ID, AFK_DATA_PATH, CANAL_ANUNCIOS_ID

log = logging.getLogger(__name__)

# ── Defaults ──────────────────────────────────────────────────────────────
DEFAULT_AFK_TIMEOUT: int = 900          # 15 minutos
DEFAULT_VERIFICATION_TIMEOUT: int = 30  # segundos
LOOP_INTERVAL: int = 20                 # loop cada 20s
WEEKLY_HOUR: int = 0                    # 00:00
WEEKLY_MINUTE: int = 0
WEEKLY_TIMEZONE: str = "Europe/Madrid"

# ── Messages ──────────────────────────────────────────────────────────────

MSG_VERIFICATION: str = (
    "⏰ **¿Sigues ahí?**\n"
    "Te he detectado en `{guild}` con el audio **{reason}** "
    "por más de **{minutes} minutos**.\n\n"
    "✍️ **Responde cualquier cosa** en los próximos "
    "**{timeout} segundos** o te desconectaré del canal de voz. 🥖"
)

MSG_VERIFICATION_OK: str = (
    "✅ Perfecto, veo que estás ahí. No serás desconectado. 🥖\n"
    "Si vuelves a estar AFK, te enviaré otro aviso."
)

MSG_KICKED_DM: str = (
    "🔇 Has sido desconectado de `{guild}` por "
    "estar AFK (no respondiste a la verificación en {timeout}s). "
    "Vuelve cuando estés activo. 🥖\n\n"
    "📊 Llevas **{strikes} expulsión(es)** esta semana."
)

# Public shame messages — randomised
PUBLIC_SHAME: List[str] = [
    "El puto subnormal de {user} ha intentado farmear horas en el canal de voz 🤣🤣🤣",
    "🚨 ¡FARMER DETECTADO! {user} estaba mode on 🔇 todo el día. A tomar por culo 🤣",
    "{user} pensaba que nadie se daba cuenta... 15 minutos ensordecido. 🤡🤡🤡",
    "📡 RADAR AFK: {user} cazado farmeando. Expulsado con honores. 🏆🤣",
    "Otro que se piensa que esto es una granja. {user} a la calle. 🦶🤣",
    "El afk más largo de {user} fue hoy... y no voluntariamente. 🤣💀",
    "⚠️ AVISO A LA FLOTA: {user} intentó colarse. Fail detectado. 🚫🤣",
    "{user} ha sido sacrificado en nombre del anti-farming. 🥖🤣",
]

MSG_NO_PERMS: str = (
    "⚠️ **AFK:** No tengo permisos para desconectar "
    "a {user} en `{channel}`."
)

# Weekly top template
MSG_WEEKLY_TOP_TITLE: str = "📊 **TOP FARMERS DE LA SEMANA** 📊"


class AFKDetection(commands.Cog):
    """Detecta y expulsa farmers de canales de voz."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._data: Dict[str, Any] = {}
        self._load_data()
        self._save_pending: bool = False
        self._initialized: bool = False

    # ═══════════════════════════════════════════════════════════════════════
    #  PERSISTENCE
    # ═══════════════════════════════════════════════════════════════════════

    def _load_data(self) -> None:
        """Load all AFK data from JSON."""
        if AFK_DATA_PATH.exists():
            try:
                with open(AFK_DATA_PATH, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                log.info("AFK: Datos cargados (%d guilds)", len(self._data.get("settings", {})))
            except (json.JSONDecodeError, OSError) as e:
                log.warning("AFK: Error cargando datos: %s — usando defaults", e)
                self._data = {}
        else:
            self._data = {}
            log.info("AFK: No hay datos previos — empezando fresh")

        # Ensure nested dicts exist
        self._data.setdefault("settings", {})
        self._data.setdefault("tracking", {})
        self._data.setdefault("pending", {})
        self._data.setdefault("strikes", {})
        self._data.setdefault("weekly_published", "")

    def _save_data(self) -> None:
        """Save all AFK data to JSON atomically."""
        temp = AFK_DATA_PATH.with_suffix(".tmp")
        try:
            with open(temp, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            temp.replace(AFK_DATA_PATH)
        except OSError as e:
            log.error("AFK: Error guardando datos: %s", e)

    def _save_later(self) -> None:
        """Flag data to be saved on the next loop iteration."""
        self._save_pending = True

    # ── Guild settings ────────────────────────────────────────────────────

    def _guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get or create settings for a guild."""
        gid = str(guild_id)
        if gid not in self._data["settings"]:
            self._data["settings"][gid] = {
                "enabled": True,
                "afk_timeout": DEFAULT_AFK_TIMEOUT,
                "verification_timeout": DEFAULT_VERIFICATION_TIMEOUT,
                "excluded_channels": [],
                "whitelist_roles": [],
            }
        return self._data["settings"][gid]

    # ── Tracking helpers ──────────────────────────────────────────────────

    def _guild_tracking(self, guild_id: int) -> Dict[str, Any]:
        """Get or create tracking dict for a guild."""
        gid = str(guild_id)
        if gid not in self._data["tracking"]:
            self._data["tracking"][gid] = {}
        return self._data["tracking"][gid]

    def _track_user(self, guild_id: int, user_id: int, channel_id: int) -> None:
        tracking = self._guild_tracking(guild_id)
        tracking[str(user_id)] = {
            "channel_id": channel_id,
            "joined_at": time.time(),
            "self_muted_since": None,
            "self_deafened_since": None,
        }

    def _untrack_user(self, guild_id: int, user_id: int) -> None:
        self._guild_tracking(guild_id).pop(str(user_id), None)

    def _update_track(self, guild_id: int, user_id: int, key: str, value: Optional[float]) -> None:
        entry = self._guild_tracking(guild_id).get(str(user_id))
        if entry:
            entry[key] = value

    def _pending_key(self, guild_id: int, user_id: int) -> str:
        return f"{guild_id}_{user_id}"

    def _is_excluded(self, guild_id: int, member: discord.Member, channel_id: int) -> bool:
        """Check if a user or channel should be excluded from AFK detection."""
        settings = self._guild_settings(guild_id)

        # Excluded channel?
        if channel_id in settings.get("excluded_channels", []):
            return True

        # Whitelisted role?
        for role in member.roles:
            if role.id in settings.get("whitelist_roles", []):
                return True

        return False

    # ── Strikes ───────────────────────────────────────────────────────────

    def _guild_strikes(self, guild_id: int) -> Dict[str, Any]:
        """Get or create strikes dict for a guild."""
        gid = str(guild_id)
        if gid not in self._data["strikes"]:
            self._data["strikes"][gid] = {}
        return self._data["strikes"][gid]

    def _add_strike(self, guild_id: int, user_id: int) -> Tuple[int, int]:
        """Add a strike and return (weekly_count, total_count)."""
        strikes = self._guild_strikes(guild_id)
        uid = str(user_id)
        if uid not in strikes:
            strikes[uid] = {"weekly": 0, "total": 0, "last_kick": 0}
        strikes[uid]["weekly"] += 1
        strikes[uid]["total"] += 1
        strikes[uid]["last_kick"] = time.time()
        self._save_later()
        return strikes[uid]["weekly"], strikes[uid]["total"]

    def _get_user_strikes(self, guild_id: int, user_id: int) -> Tuple[int, int, float]:
        """Get (weekly, total, last_kick) for a user."""
        strikes = self._guild_strikes(guild_id)
        uid = str(user_id)
        if uid not in strikes:
            return 0, 0, 0
        s = strikes[uid]
        return s.get("weekly", 0), s.get("total", 0), s.get("last_kick", 0)

    def _get_weekly_top(self, guild_id: int, limit: int = 10) -> List[Tuple[int, int]]:
        """Get top farmers this week sorted by weekly strikes desc."""
        strikes = self._guild_strikes(guild_id)
        ranked = [(int(uid), s["weekly"]) for uid, s in strikes.items() if s["weekly"] > 0]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:limit]

    def _reset_weekly_strikes(self) -> None:
        """Reset weekly counts for all guilds."""
        for gid, guild_strikes in self._data["strikes"].items():
            for uid in guild_strikes:
                guild_strikes[uid]["weekly"] = 0
        self._data["weekly_published"] = ""
        self._save_data()
        log.info("AFK: Strikes semanales reseteados")

    # ═══════════════════════════════════════════════════════════════════════
    #  LIFE CYCLE
    # ═══════════════════════════════════════════════════════════════════════

    async def cog_load(self) -> None:
        self.afk_loop.start()
        self.weekly_top_loop.start()
        log.info("AFK: Cog cargado")

    async def cog_unload(self) -> None:
        self.afk_loop.stop()
        self.weekly_top_loop.stop()
        self._save_data()
        log.info("AFK: Cog descargado")

    # ═══════════════════════════════════════════════════════════════════════
    #  LOOPS
    # ═══════════════════════════════════════════════════════════════════════

    @tasks.loop(seconds=LOOP_INTERVAL)
    async def afk_loop(self) -> None:
        """Main AFK detection loop."""
        # Initialize tracking on first run (catch users already in VC)
        if not self._initialized:
            await self._init_tracking()
            self._initialized = True

        # Save if flagged
        if self._save_pending:
            self._save_data()
            self._save_pending = False

        now = time.time()

        for guild in self.bot.guilds:
            try:
                gid = guild.id
                settings = self._guild_settings(gid)
                if not settings["enabled"]:
                    continue

                tracking = self._guild_tracking(gid)

                # 1. New candidates → send verification DMs
                for uid_str, data in list(tracking.items()):
                    uid = int(uid_str)

                    # Already pending?
                    pkey = self._pending_key(gid, uid)
                    if pkey in self._data["pending"]:
                        continue

                    # Excluded?
                    member = guild.get_member(uid)
                    if not member:
                        continue
                    channel_id = data.get("channel_id")
                    if self._is_excluded(gid, member, channel_id):
                        continue

                    # Check AFK status
                    is_afk, reason, since = self._check_afk(data, now, settings["afk_timeout"])
                    if is_afk:
                        await self._send_verification(member, guild, reason, since)

                # 2. Expired verifications → kick
                for pkey, pinfo in list(self._data["pending"].items()):
                    # Only process pending items for THIS guild
                    if int(pinfo.get("guild_id", 0)) != gid:
                        continue
                    if now - pinfo["ts"] >= settings["verification_timeout"]:
                        uid = int(pinfo["user_id"])
                        guild_id = int(pinfo["guild_id"])
                        member = guild.get_member(uid)
                        if member:
                            await self._kick_afk_user(member, guild)
                        else:
                            self._data["pending"].pop(pkey, None)
                            self._untrack_user(guild_id, uid)

            except Exception as exc:
                log.error("AFK: Error en guild %s: %s", guild.name, exc, exc_info=True)

    async def _init_tracking(self) -> None:
        """Catch up — track users already in voice channels on startup."""
        tracked = 0
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                for member in channel.members:
                    if member.bot:
                        continue
                    self._track_user(guild.id, member.id, channel.id)
                    vs = member.voice
                    if vs and vs.self_mute:
                        self._update_track(guild.id, member.id, "self_muted_since", time.time())
                    if vs and vs.self_deaf:
                        self._update_track(guild.id, member.id, "self_deafened_since", time.time())
                    tracked += 1
        log.info("AFK: Seguimiento iniciado — %d usuarios en VC", tracked)

    @afk_loop.before_loop
    async def before_afk_loop(self) -> None:
        await self.bot.wait_until_ready()

    # ── Weekly top ────────────────────────────────────────────────────────

    @tasks.loop(minutes=30)
    async def weekly_top_loop(self) -> None:
        """Check every 30 min if it's Sunday 00:00 Spain time."""
        tz = pytz.timezone(WEEKLY_TIMEZONE)
        now = datetime.now(tz)

        if now.weekday() == 6 and now.hour == WEEKLY_HOUR and now.minute == WEEKLY_MINUTE:
            # Check if already published this week
            week_key = now.strftime("%Y-W%W")
            if self._data.get("weekly_published") != week_key:
                await self._publish_weekly_top()
                self._data["weekly_published"] = week_key
                self._save_data()

    @weekly_top_loop.before_loop
    async def before_weekly_loop(self) -> None:
        await self.bot.wait_until_ready()

    async def _publish_weekly_top(self) -> None:
        """Post the weekly farmer leaderboard to announcements."""
        canal = self.bot.get_channel(CANAL_ANUNCIOS_ID)
        if not canal:
            log.warning("AFK: No se encuentra CANAL_ANUNCIOS_ID para publicar top semanal")
            return

        for guild in self.bot.guilds:
            top = self._get_weekly_top(guild.id, limit=10)
            if not top:
                continue

            lines = []
            medals = ["🥇", "🥈", "🥉"]
            for i, (uid, count) in enumerate(top):
                med = medals[i] if i < 3 else f"#{i+1}"
                member = guild.get_member(uid)
                name = f"**{member.display_name}**" if member else f"`ID:{uid}`"
                lines.append(f"{med} {name} — **{count}** expulsión(es)")

            if not lines:
                continue

            embed = discord.Embed(
                title=MSG_WEEKLY_TOP_TITLE,
                description="\n".join(lines),
                color=discord.Color.red(),
            )
            embed.set_footer(text="🥖 Teto anti-farming system • Reseteo semanal")
            await canal.send(embed=embed)
            log.info("AFK: Top semanal publicado para %s (%d farmers)", guild.name, len(top))

        # Reset all weekly strikes
        self._reset_weekly_strikes()

    # ═══════════════════════════════════════════════════════════════════════
    #  VOICE STATE LISTENER
    # ═══════════════════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        if member.bot:
            return

        gid = member.guild.id
        uid = member.id

        # ── Joined ──
        if before.channel is None and after.channel is not None:
            self._track_user(gid, uid, after.channel.id)
            if after.self_mute:
                self._update_track(gid, uid, "self_muted_since", time.time())
            if after.self_deaf:
                self._update_track(gid, uid, "self_deafened_since", time.time())
            self._save_later()
            return

        # ── Left ──
        if before.channel is not None and after.channel is None:
            self._untrack_user(gid, uid)
            self._data["pending"].pop(self._pending_key(gid, uid), None)
            self._save_later()
            return

        # ── Moved ──
        if before.channel is not None and after.channel is not None and before.channel != after.channel:
            self._update_track(gid, uid, "channel_id", after.channel.id)

        # ── Self-mute ──
        if before.self_mute != after.self_mute:
            if after.self_mute:
                self._update_track(gid, uid, "self_muted_since", time.time())
            else:
                self._update_track(gid, uid, "self_muted_since", None)
                self._data["pending"].pop(self._pending_key(gid, uid), None)
            self._save_later()

        # ── Self-deafen ──
        if before.self_deaf != after.self_deaf:
            if after.self_deaf:
                self._update_track(gid, uid, "self_deafened_since", time.time())
            else:
                self._update_track(gid, uid, "self_deafened_since", None)
                self._data["pending"].pop(self._pending_key(gid, uid), None)
            self._save_later()

    # ═══════════════════════════════════════════════════════════════════════
    #  DM VERIFICATION LISTENER
    # ═══════════════════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if not isinstance(message.channel, discord.DMChannel):
            return

        uid = message.author.id
        # Check all pending — find any for this user
        found = None
        for pkey, pinfo in list(self._data["pending"].items()):
            if int(pinfo["user_id"]) == uid:
                found = pkey
                break

        if found:
            self._data["pending"].pop(found, None)
            self._save_later()
            await message.channel.send(MSG_VERIFICATION_OK)
            log.info("AFK: %s respondió verificación — cancelado", message.author.display_name)

    # ═══════════════════════════════════════════════════════════════════════
    #  AFK LOGIC
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _check_afk(data: dict, now: float, timeout: int) -> Tuple[bool, str, float]:
        """Check if a tracked user qualifies as AFK."""
        since_deaf: Optional[float] = data.get("self_deafened_since")
        since_mute: Optional[float] = data.get("self_muted_since")

        deaf_ok = since_deaf is not None and (now - since_deaf) >= timeout
        mute_ok = since_mute is not None and (now - since_mute) >= timeout

        if deaf_ok and mute_ok:
            if since_deaf <= since_mute:
                return True, "ensordecido/a", since_deaf
            return True, "silenciado/a", since_mute
        if deaf_ok:
            return True, "ensordecido/a", since_deaf
        if mute_ok:
            return True, "silenciado/a", since_mute
        return False, "", 0

    # ═══════════════════════════════════════════════════════════════════════
    #  ACTIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def _send_verification(self, member: discord.Member, guild: discord.Guild,
                                  reason: str, since: float) -> None:
        settings = self._guild_settings(guild.id)
        minutes = int((time.time() - since) / 60)

        try:
            await member.send(
                MSG_VERIFICATION.format(
                    mention=member.mention,
                    guild=guild.name,
                    reason=reason,
                    minutes=minutes,
                    timeout=settings["verification_timeout"],
                )
            )
            pkey = self._pending_key(guild.id, member.id)
            self._data["pending"][pkey] = {
                "guild_id": guild.id,
                "user_id": member.id,
                "ts": time.time(),
            }
            self._save_later()
            log.info("AFK: Verif a %s (%s, %d min)", member.display_name, reason, minutes)
        except discord.Forbidden:
            log.warning("AFK: DMs cerrados %s — kick directo", member.display_name)
            await self._kick_afk_user(member, guild, reason="DMs cerrados")

    async def _kick_afk_user(self, member: discord.Member, guild: discord.Guild,
                              reason: str = "No respondió a verificación") -> None:
        if not member.voice:
            self._untrack_user(guild.id, member.id)
            self._data["pending"].pop(self._pending_key(guild.id, member.id), None)
            self._save_later()
            return

        channel_name = member.voice.channel.name if member.voice.channel else "desconocido"

        try:
            await member.move_to(None, reason=f"[AFK Detection] {reason}")
            self._untrack_user(guild.id, member.id)
            self._data["pending"].pop(self._pending_key(guild.id, member.id), None)

            # Add strike
            weekly, total = self._add_strike(guild.id, member.id)

            log.info("AFK: %s echado de #%s (%s) — strikes: %dW/%dT",
                     member.display_name, channel_name, reason, weekly, total)

            # DM user
            try:
                await member.send(
                    MSG_KICKED_DM.format(
                        guild=guild.name,
                        timeout=self._guild_settings(guild.id)["verification_timeout"],
                        strikes=weekly,
                    )
                )
            except discord.Forbidden:
                pass

            # Public shame
            canal = self.bot.get_channel(CANAL_ANUNCIOS_ID)
            if canal:
                try:
                    msg = random.choice(PUBLIC_SHAME).format(user=member.mention)
                    await canal.send(msg)
                except discord.DiscordException:
                    pass

        except discord.Forbidden:
            log.warning("AFK: Sin permisos para %s en %s", member.display_name, guild.name)
            canal = self.bot.get_channel(CANAL_ANUNCIOS_ID)
            if canal:
                try:
                    await canal.send(
                        MSG_NO_PERMS.format(user=member.mention, channel=channel_name)
                    )
                except discord.DiscordException:
                    pass

        except discord.DiscordException as e:
            log.error("AFK: Error al echar a %s: %s", member.display_name, e)
        else:
            self._save_later()

    # ═══════════════════════════════════════════════════════════════════════
    #  COMMAND: afkgest GROUP
    # ═══════════════════════════════════════════════════════════════════════

    @commands.group(name="afkgest", aliases=["afkg", "ag"])
    async def afkgest(self, ctx: commands.Context) -> None:
        """[Admin] Gestión del sistema anti-AFK. Usa: cx!afkgest <subcomando>"""
        if ctx.author.id != ADMIN_ID:
            return
        if ctx.invoked_subcommand is None:
            cmds = (
                "**Subcomandos:**\n"
                "`status` — Estado general\n"
                "`toggle` — Activar/desactivar\n"
                "`timeout <min>` — Tiempo AFK antes de verificar\n"
                "`exclude #canal` — Excluir canal de voz\n"
                "`include #canal` — Incluir canal de vuelta\n"
                "`excluded` — Canales excluidos\n"
                "`whitelist add @rol` — Añadir rol a whitelist\n"
                "`whitelist remove @rol` — Quitar rol\n"
                "`whitelist` — Listar whitelist\n"
                "`strikes [@user]` — Ver strikes de alguien\n"
                "`striketop` — Top farmers de la semana"
            )
            await ctx.send(cmds)

    # ── status ────────────────────────────────────────────────────────────

    @afkgest.command(name="status")
    async def afkgest_status(self, ctx: commands.Context) -> None:
        """Estado actual del sistema."""
        if ctx.author.id != ADMIN_ID:
            return
        settings = self._guild_settings(ctx.guild.id)
        tracking = self._guild_tracking(ctx.guild.id)
        total_pending = sum(1 for p in self._data["pending"].values() if int(p["guild_id"]) == ctx.guild.id)
        excluded = settings.get("excluded_channels", [])
        whitelist = settings.get("whitelist_roles", [])

        embed = discord.Embed(
            title="🎧 Sistema Anti-AFK",
            color=discord.Color.green() if settings["enabled"] else discord.Color.red(),
        )
        embed.add_field(name="⚙️ Estado", value="🟢 Activo" if settings["enabled"] else "🔴 Desactivado", inline=True)
        embed.add_field(name="⏱️ Timeout AFK", value=f"`{settings['afk_timeout'] // 60} min`", inline=True)
        embed.add_field(name="⏳ Verificación", value=f"`{settings['verification_timeout']}s`", inline=True)
        embed.add_field(name="📊 En VC", value=f"`{len(tracking)}` usuarios", inline=True)
        embed.add_field(name="⏳ Pendientes", value=f"`{total_pending}`", inline=True)
        embed.add_field(name="🔇 Canales excluidos", value=f"`{len(excluded)}`", inline=True)
        embed.add_field(name="🛡️ Roles whitelist", value=f"`{len(whitelist)}`", inline=True)

        # Show tracked users
        if tracking:
            now = time.time()
            lines = []
            for uid_str, data in list(tracking.items())[:15]:
                uid = int(uid_str)
                m = ctx.guild.get_member(uid)
                name = m.display_name if m else f"ID:{uid}"
                is_afk, reason, since = self._check_afk(data, now, settings["afk_timeout"])
                if is_afk:
                    mins = int((now - since) / 60)
                    status = f"🔇 **{reason}** ({mins} min)"
                else:
                    sd = data.get("self_deafened_since")
                    sm = data.get("self_muted_since")
                    if sd:
                        mins = int((now - sd) / 60)
                        status = f"🔇 ensordecido ({mins} min)"
                    elif sm:
                        mins = int((now - sm) / 60)
                        status = f"🔇 silenciado ({mins} min)"
                    else:
                        status = "🎤 activo"
                pkey = self._pending_key(ctx.guild.id, uid)
                pend = " ⏳" if pkey in self._data["pending"] else ""
                lines.append(f"• {name} — {status}{pend}")
            if lines:
                embed.add_field(name="📋 Usuarios", value="\n".join(lines), inline=False)

        # Show strike stats
        w_total = sum(s["weekly"] for s in self._data["strikes"].get(str(ctx.guild.id), {}).values())
        t_total = sum(s["total"] for s in self._data["strikes"].get(str(ctx.guild.id), {}).values())
        embed.add_field(name="💥 Expulsiones esta semana", value=f"`{w_total}`", inline=True)
        embed.add_field(name="💀 Expulsiones totales", value=f"`{t_total}`", inline=True)

        await ctx.send(embed=embed)

    # ── toggle ────────────────────────────────────────────────────────────

    @afkgest.command(name="toggle")
    async def afkgest_toggle(self, ctx: commands.Context) -> None:
        """Activar/desactivar detección."""
        if ctx.author.id != ADMIN_ID:
            return
        settings = self._guild_settings(ctx.guild.id)
        settings["enabled"] = not settings["enabled"]
        self._save_later()
        estado = "🟢 **ACTIVADO**" if settings["enabled"] else "🔴 **DESACTIVADO**"
        await ctx.send(f"🎧 Sistema Anti-AFK {estado}")
        log.info("AFK: toggle %s por %s", "ON" if settings["enabled"] else "OFF", ctx.author)

    # ── timeout ───────────────────────────────────────────────────────────

    @afkgest.command(name="timeout")
    async def afkgest_timeout(self, ctx: commands.Context, minutos: int) -> None:
        """Cambiar tiempo AFK (minutos). Ej: cx!afkgest timeout 10"""
        if ctx.author.id != ADMIN_ID:
            return
        if minutos < 1 or minutos > 120:
            await ctx.send("❌ Elige entre 1 y 120 minutos.")
            return
        settings = self._guild_settings(ctx.guild.id)
        settings["afk_timeout"] = minutos * 60
        self._save_later()
        await ctx.send(f"✅ Tiempo AFK cambiado a **{minutos} minutos**.")

    # ── exclude ───────────────────────────────────────────────────────────

    @afkgest.command(name="exclude")
    async def afkgest_exclude(self, ctx: commands.Context, canal: discord.VoiceChannel) -> None:
        """Excluir un canal de voz de la detección."""
        if ctx.author.id != ADMIN_ID:
            return
        settings = self._guild_settings(ctx.guild.id)
        if canal.id in settings["excluded_channels"]:
            await ctx.send(f"⚠️ {canal.mention} ya está excluido.")
            return
        settings["excluded_channels"].append(canal.id)
        self._save_later()
        await ctx.send(f"✅ {canal.mention} excluido de la detección AFK.")

    @afkgest.command(name="include")
    async def afkgest_include(self, ctx: commands.Context, canal: discord.VoiceChannel) -> None:
        """Reincluir un canal de voz en la detección."""
        if ctx.author.id != ADMIN_ID:
            return
        settings = self._guild_settings(ctx.guild.id)
        if canal.id not in settings["excluded_channels"]:
            await ctx.send(f"⚠️ {canal.mention} no está excluido.")
            return
        settings["excluded_channels"].remove(canal.id)
        self._save_later()
        await ctx.send(f"✅ {canal.mention} reincluido en la detección AFK.")

    @afkgest.command(name="excluded")
    async def afkgest_excluded(self, ctx: commands.Context) -> None:
        """Listar canales excluidos."""
        if ctx.author.id != ADMIN_ID:
            return
        settings = self._guild_settings(ctx.guild.id)
        excluded = settings.get("excluded_channels", [])
        if not excluded:
            await ctx.send("📋 No hay canales excluidos.")
            return
        lines = []
        for cid in excluded:
            c = ctx.guild.get_channel(cid)
            lines.append(f"• {c.mention if c else f'`ID:{cid}`'}")
        await ctx.send("🔇 **Canales excluidos:**\n" + "\n".join(lines))

    # ── whitelist ─────────────────────────────────────────────────────────

    @afkgest.group(name="whitelist")
    async def afkgest_whitelist(self, ctx: commands.Context) -> None:
        """Gestionar whitelist de roles. Subcomandos: add, remove."""
        if ctx.author.id != ADMIN_ID:
            return
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcomandos: `cx!afkgest whitelist add @rol`, `remove @rol`")

    @afkgest_whitelist.command(name="add")
    async def whitelist_add(self, ctx: commands.Context, rol: discord.Role) -> None:
        """Añadir rol a la whitelist (no será detectado como AFK)."""
        if ctx.author.id != ADMIN_ID:
            return
        settings = self._guild_settings(ctx.guild.id)
        if rol.id in settings["whitelist_roles"]:
            await ctx.send(f"⚠️ {rol.mention} ya está en la whitelist.")
            return
        settings["whitelist_roles"].append(rol.id)
        self._save_later()
        await ctx.send(f"✅ {rol.mention} añadido a la whitelist AFK.")

    @afkgest_whitelist.command(name="remove")
    async def whitelist_remove(self, ctx: commands.Context, rol: discord.Role) -> None:
        """Quitar rol de la whitelist."""
        if ctx.author.id != ADMIN_ID:
            return
        settings = self._guild_settings(ctx.guild.id)
        if rol.id not in settings["whitelist_roles"]:
            await ctx.send(f"⚠️ {rol.mention} no está en la whitelist.")
            return
        settings["whitelist_roles"].remove(rol.id)
        self._save_later()
        await ctx.send(f"✅ {rol.mention} quitado de la whitelist AFK.")

    @afkgest_whitelist.command(name="list")
    async def whitelist_list(self, ctx: commands.Context) -> None:
        """Listar roles en whitelist."""
        if ctx.author.id != ADMIN_ID:
            return
        settings = self._guild_settings(ctx.guild.id)
        roles = settings.get("whitelist_roles", [])
        if not roles:
            await ctx.send("📋 No hay roles en la whitelist.")
            return
        lines = []
        for rid in roles:
            r = ctx.guild.get_role(rid)
            lines.append(f"• {r.mention if r else f'`ID:{rid}`'}")
        await ctx.send("🛡️ **Roles whitelist:**\n" + "\n".join(lines))

    # ── strikes ───────────────────────────────────────────────────────────

    @afkgest.command(name="strikes")
    async def afkgest_strikes(self, ctx: commands.Context, miembro: Optional[discord.Member] = None) -> None:
        """Ver strikes de un usuario o los tuyos."""
        if ctx.author.id != ADMIN_ID:
            return
        miembro = miembro or ctx.author
        weekly, total, last = self._get_user_strikes(ctx.guild.id, miembro.id)

        embed = discord.Embed(
            title=f"💥 Strikes de {miembro.display_name}",
            color=discord.Color.red() if weekly > 0 else discord.Color.green(),
        )
        embed.add_field(name="📅 Esta semana", value=f"`{weekly}` expulsiones", inline=True)
        embed.add_field(name="💀 Totales", value=f"`{total}` expulsiones", inline=True)
        if last:
            embed.add_field(name="🕐 Última", value=f"<t:{int(last)}:R>", inline=True)
        await ctx.send(embed=embed)

    @afkgest.command(name="striketop", aliases=["strikes_top", "farmertop"])
    async def afkgest_striketop(self, ctx: commands.Context) -> None:
        """Top farmers de la semana."""
        if ctx.author.id != ADMIN_ID:
            return
        top = self._get_weekly_top(ctx.guild.id, limit=15)
        if not top:
            await ctx.send("🎉 **No hay farmers esta semana.** Bien jugado, equipo.")
            return

        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for i, (uid, count) in enumerate(top):
            med = medals[i] if i < 3 else f"#{i+1}"
            member = ctx.guild.get_member(uid)
            name = f"**{member.display_name}**" if member else f"`ID:{uid}`"
            lines.append(f"{med} {name} — **{count}** expulsión(es)")

        embed = discord.Embed(
            title="📊 TOP FARMERS DE LA SEMANA",
            description="\n".join(lines),
            color=discord.Color.red(),
        )
        embed.set_footer(text="🥖 Se resetea cada domingo a las 00:00")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Load the AFK Detection cog."""
    await bot.add_cog(AFKDetection(bot))
