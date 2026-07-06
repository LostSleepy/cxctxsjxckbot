"""
Utility commands cog for the Teto Discord bot.
Includes ping, 8ball, avatar, userinfo, ship, uptime, hora, help, and more.
"""
import json
import logging
import random
import time
from datetime import datetime
from typing import List, Optional

import discord
import pytz
from discord.ext import commands

from config import ADMIN_ID, SHIP_DATA_PATH

log = logging.getLogger(__name__)


def _cargar_ship_data() -> dict:
    """Load ship compatibility data from JSON file."""
    if not SHIP_DATA_PATH.exists():
        return {}
    try:
        with open(SHIP_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _guardar_ship_data(data: dict) -> None:
    """Save ship compatibility data to JSON file atomically."""
    temp = SHIP_DATA_PATH.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp.replace(SHIP_DATA_PATH)


class Utilidad(commands.Cog):
    """Utility and general-purpose commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._start_time: float = time.time()

    async def _bypass_cooldown(self, ctx: commands.Context) -> None:
        """Remove cooldown for the configured admin."""
        if ctx.author.id == ADMIN_ID:
            ctx.command.reset_cooldown(ctx)

    # ── Ping ──────────────────────────────────────────────────────────────────
    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context) -> None:
        """Check bot latency and API response time."""
        start = time.time()
        msg = await ctx.send("🏓 Poneando...")
        api_ms = round(self.bot.latency * 1000)
        web_ms = round((time.time() - start) * 1000)
        await msg.edit(
            content=(
                f"**¡Pong!** 🏓\n"
                f"**Latencia API:** `{api_ms}ms`\n"
                f"**Respuesta Web:** `{web_ms}ms`"
            )
        )

    # ── 8Ball ────────────────────────────────────────────────────────────────
    @commands.command(name="8ball", aliases=["pregunta", "ball"])
    async def eight_ball(self, ctx: commands.Context, *, pregunta: str) -> None:
        """Consult the mystical 8ball."""
        respuestas: List[str] = [
            "Claramente sí. ✅",
            "Es decididamente así. ✨",
            "Sin ninguna duda. 💎",
            "Pregunta en otro momento... ⏳",
            "Mejor no te lo digo ahora. 🤐",
            "Mis fuentes dicen que no. ❌",
            "Las perspectivas no son buenas. 📉",
            "Muy dudoso. 🤔",
            "¡Por supuesto! 🚀",
            "No cuentes con ello. 🛑",
        ]
        embed = discord.Embed(
            title="🎱 La Bola 8 Mística",
            color=discord.Color.dark_blue(),
        )
        embed.add_field(name="Pregunta:", value=f"*{pregunta}*", inline=False)
        embed.add_field(
            name="Respuesta:",
            value=f"**{random.choice(respuestas)}**",
            inline=False,
        )
        embed.set_footer(
            text=f"Solicitado por {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )
        await ctx.send(embed=embed)

    # ── Elegir ───────────────────────────────────────────────────────────────
    @commands.command(name="elegir")
    async def elegir(self, ctx: commands.Context, *, opciones: str) -> None:
        """Pick randomly between comma-separated options."""
        lista: List[str] = [o.strip() for o in opciones.split(",")]
        if len(lista) < 2:
            await ctx.send(
                "Pon al menos dos opciones separadas por coma. "
                "Ej: `cx!elegir pizza, hamburguesa`."
            )
            return
        await ctx.send(
            f"🤔 Después de mucho pensar, elijo: **{random.choice(lista)}**"
        )

    # ── Avatar ───────────────────────────────────────────────────────────────
    @commands.command(name="avatar", aliases=["av"])
    async def avatar(
        self, ctx: commands.Context, miembro: Optional[discord.Member] = None
    ) -> None:
        """View a member's profile picture in high resolution."""
        miembro = miembro or ctx.author
        embed = discord.Embed(
            title=f"🖼️ Avatar de {miembro.name}",
            color=miembro.color,
        )
        embed.set_image(url=miembro.display_avatar.url)
        await ctx.send(embed=embed)

    # ── Userinfo ─────────────────────────────────────────────────────────────
    @commands.command(name="userinfo", aliases=["user", "info", "u"])
    async def userinfo(
        self, ctx: commands.Context, miembro: Optional[discord.Member] = None
    ) -> None:
        """Show detailed user information. Admins can add `raw` for extra info."""
        miembro = miembro or ctx.author
        # Check message content directly so `cx!userinfo raw` works without member parsing
        is_raw = ctx.author.id == ADMIN_ID and "raw" in ctx.message.content.lower().split()
        created_ts = int(miembro.created_at.timestamp())
        joined_ts = int(miembro.joined_at.timestamp())
        roles = [r.mention for r in miembro.roles if r.name != "@everyone"]

        embed = discord.Embed(
            title=f"{'🔬 Información RAW de' if is_raw else 'Información de'} {miembro.name}",
            color=miembro.color,
        )
        embed.set_thumbnail(url=miembro.display_avatar.url)
        embed.add_field(name="🆔 ID", value=f"`{miembro.id}`", inline=True)
        embed.add_field(name="🏷️ Apodo", value=miembro.display_name, inline=True)
        embed.add_field(
            name="🗓️ Cuenta creada",
            value=f"<t:{created_ts}:D> (<t:{created_ts}:R>)",
            inline=True,
        )
        embed.add_field(
            name="📥 Se unió",
            value=f"<t:{joined_ts}:D> (<t:{joined_ts}:R>)",
            inline=True,
        )
        embed.add_field(
            name="🎭 Roles",
            value=" ".join(roles) if roles else "Sin roles",
            inline=False,
        )

        if is_raw:
            # Status mapping
            status_map = {
                discord.Status.online: "🟢 Online",
                discord.Status.idle: "🟡 Idle",
                discord.Status.dnd: "🔴 DND",
                discord.Status.offline: "⚫ Offline",
            }
            status_str = status_map.get(miembro.status, "❓ Desconocido")
            avatar_hash = str(miembro.avatar.key) if miembro.avatar else "N/A"
            top_role = miembro.top_role.mention if miembro.top_role.name != "@everyone" else "Ninguno"
            perms = [perm[0].replace("_", " ").title() for perm in miembro.guild_permissions if perm[1]]
            perms_str = ", ".join(perms[:20])
            if len(perms) > 20:
                perms_str += f"\n... y {len(perms) - 20} más"

            embed.add_field(name="📡 Estado", value=status_str, inline=True)
            embed.add_field(name="🎮 Actividad", value=str(miembro.activity) if miembro.activity else "Ninguna", inline=True)
            embed.add_field(name="🎭 Top Rol", value=top_role, inline=True)
            embed.add_field(name="🖼️ Avatar Hash", value=f"`{avatar_hash}`", inline=True)
            embed.add_field(name="🤖 Bot", value="Sí" if miembro.bot else "No", inline=True)
            embed.add_field(name="🎨 Color", value=f"`#{miembro.color.value:06X}`", inline=True)
            embed.add_field(name="🔑 Permisos", value=perms_str if perms else "Ninguno", inline=False)

            # Aura (from extras cog)
            extras_cog = self.bot.get_cog("Extras")
            if extras_cog and hasattr(extras_cog, "aura_manager"):
                aura = await extras_cog.aura_manager.get_aura(str(miembro.id))
                embed.add_field(name="✨ Aura", value=f"`{aura} pts`", inline=True)

            embed.set_footer(text="⚠️ Información solo visible para el admin", icon_url=ctx.author.display_avatar.url)
        else:
            embed.set_footer(text=f"Solicitado por {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ── Hora ─────────────────────────────────────────────────────────────────
    @commands.command(name="hora")
    async def hora(self, ctx: commands.Context) -> None:
        """Show world clock for Madrid, New York, and Japan."""
        zonas: dict = {
            "🇪🇸 Madrid": "Europe/Madrid",
            "🇯🇵 Japón": "Asia/Tokyo",
            "🇺🇸 NY": "America/New_York",
        }
        embed = discord.Embed(
            title="⌚ Reloj Mundial",
            color=discord.Color.blue(),
        )
        for nombre, zona in zonas.items():
            hora_actual = datetime.now(pytz.timezone(zona)).strftime("%H:%M")
            embed.add_field(name=nombre, value=f"**{hora_actual}**", inline=True)
        await ctx.send(embed=embed)

    # ── Ship ─────────────────────────────────────────────────────────────────
    @commands.command(name="ship")
    async def ship(
        self,
        ctx: commands.Context,
        usuario1: discord.Member,
        usuario2: Optional[discord.Member] = None,
    ) -> None:
        """Calculate love compatibility between two users (persistent)."""
        usuario2 = usuario2 or ctx.author
        if usuario2 == usuario1:
            usuario2 = ctx.author

        # Build a consistent key from sorted IDs so (A,B) == (B,A)
        id_a, id_b = sorted((usuario1.id, usuario2.id))
        key = f"{id_a}-{id_b}"

        # Load existing data
        data = _cargar_ship_data()

        if key in data:
            porcentaje = data[key]
        else:
            porcentaje = random.randint(0, 100)
            data[key] = porcentaje
            _guardar_ship_data(data)

        barra = "❤️" * (porcentaje // 10) + "🖤" * (10 - porcentaje // 10)

        embed = discord.Embed(
            title="💘 Calculadora de Amor",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="Pareja",
            value=f"{usuario1.mention} & {usuario2.mention}",
            inline=False,
        )
        embed.add_field(
            name="Compatibilidad",
            value=f"{porcentaje}%\n{barra}",
            inline=False,
        )
        embed.set_footer(text="💞 Este valor es permanente para esta pareja.")
        await ctx.send(embed=embed)

    # ── Uptime ───────────────────────────────────────────────────────────────
    @commands.command(name="uptime")
    async def uptime(self, ctx: commands.Context) -> None:
        """Show how long the bot has been running."""
        diff = int(round(time.time() - self._start_time))
        minutes, seconds = divmod(diff, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"🕒 **Uptime:** `{days}d {hours}h {minutes}m {seconds}s`")

    # ── Teto ─────────────────────────────────────────────────────────────────
    @commands.command(name="teto")
    async def teto(self, ctx: commands.Context) -> None:
        """🥖"""
        await ctx.send(
            "**🥖 ¡Teto, yay!**\n"
            "https://cdn.discordapp.com/attachments/874124605533614090/"
            "1478366865201037353/pFw1Rzg.mp4"
        )

    # ── Definir (dictionary lookup) ──────────────────────────────────────────
    @commands.command(name="definir", aliases=["define", "dict"])
    async def definir(self, ctx: commands.Context, *, palabra: str) -> None:
        """📖 Look up a word's definition. Tries Spanish first, falls back to English."""
        from utils.dictionary import lookup_word

        if not palabra or not palabra.strip():
            await ctx.send(
                "❌ Uso: `cx!definir <palabra>` (ej: `cx!definir casa`)"
            )
            return

        async with ctx.typing():
            definitions = await lookup_word(palabra)

        if not definitions:
            embed = discord.Embed(
                title=f"📖 {palabra}",
                description=(
                    "No encontré definiciones. "
                    "Prueba otra palabra o comprueba la ortografía."
                ),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"📖 Definición de {palabra}",
            description="\n".join(f"• {d}" for d in definitions),
            color=discord.Color.blue(),
        )
        embed.set_footer(
            text="FreeDictionaryAPI • ES → EN fallback",
            icon_url=ctx.author.display_avatar.url,
        )
        await ctx.send(embed=embed)

    # ── Mute All (admin only) ────────────────────────────────────────────────
    @commands.command(name="muteall")
    async def mute_all(self, ctx: commands.Context) -> None:
        """[Admin] Mute everyone in your voice channel."""
        if ctx.author.id != ADMIN_ID:
            return
        if not ctx.author.voice:
            await ctx.send("❌ Entra en un canal de voz primero.")
            return
        count = 0
        for miembro in ctx.author.voice.channel.members:
            if miembro.bot or miembro.id == ADMIN_ID:
                continue
            try:
                await miembro.edit(mute=True)
                count += 1
            except discord.DiscordException:
                pass
        await ctx.send(f"🔇 {count} usuarios silenciados.")

    # ── Unmute All (admin only) ──────────────────────────────────────────────
    @commands.command(name="unmuteall")
    async def unmute_all(self, ctx: commands.Context) -> None:
        """[Admin] Unmute everyone in your voice channel."""
        if ctx.author.id != ADMIN_ID:
            return
        if not ctx.author.voice:
            await ctx.send("❌ Entra en un canal de voz primero.")
            return
        count = 0
        for miembro in ctx.author.voice.channel.members:
            if miembro.bot:
                continue
            try:
                await miembro.edit(mute=False)
                count += 1
            except discord.DiscordException:
                pass
        await ctx.send(f"🔊 {count} usuarios dessilenciados.")

    # ── Slowmode (admin only) ──────────────────────────────────────────────
    @commands.command(name="slowmode", aliases=["sm"])
    async def slowmode(self, ctx: commands.Context, canal: Optional[discord.TextChannel] = None, segundos: Optional[int] = None) -> None:
        """[Admin] Establece el slowmode de un canal de texto."""
        if ctx.author.id != ADMIN_ID:
            return
        if canal is None or segundos is None:
            await ctx.send("❌ Usa: `cx!slowmode #canal 10` (o `0` para desactivar)")
            return
        if segundos < 0 or segundos > 21600:
            await ctx.send("❌ El slowmode debe ser entre 0 y 21600 segundos (6h).")
            return
        try:
            await canal.edit(slowmode_delay=segundos)
            if segundos == 0:
                await ctx.send(f"✅ Slowmode desactivado en {canal.mention}.")
            else:
                await ctx.send(f"✅ Slowmode en {canal.mention} establecido a **{segundos}s**.")
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para modificar ese canal.")


    # ── Servidor Info ────────────────────────────────────────────────────────
    @commands.command(name="servidor", aliases=["server", "serverinfo", "guild", "guildinfo"])
    async def servidor_info(self, ctx: commands.Context) -> None:
        """Muestra información del servidor."""
        guild = ctx.guild
        if not guild:
            await ctx.send("❌ Debes estar en un servidor para usar este comando.")
            return

        # Count bot vs human members
        total_members = guild.member_count or 0
        bots = sum(1 for m in guild.members if m.bot) if guild.members else 0
        humans = total_members - bots

        # Channel counts
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)

        embed = discord.Embed(
            title=f"📊 {guild.name}",
            description=guild.description or "Sin descripción",
            color=discord.Color.blue()
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👑 Dueño", value=guild.owner.mention if guild.owner else "Desconocido", inline=True)
        embed.add_field(name="📅 Creado", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="🆔 ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="👥 Miembros", value=f"{humans} humanos • {bots} bots", inline=True)
        embed.add_field(name="💬 Canales", value=f"{text_channels} texto • {voice_channels} voz • {categories} cat.", inline=True)
        embed.add_field(name="🚀 Boosts", value=f"{guild.premium_subscription_count} (Nivel {guild.premium_tier})", inline=True)
        embed.add_field(name="🎭 Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="😀 Emojis", value=f"{len(guild.emojis)}/{guild.emoji_limit * 2}", inline=True)

        await ctx.send(embed=embed)


    # ── Rol Info ─────────────────────────────────────────────────────────────
    @commands.command(name="rol", aliases=["role", "roleinfo", "rolinfo"])
    async def rol_info(self, ctx: commands.Context, *, rol: discord.Role = None) -> None:
        """Muestra información de un rol del servidor."""
        if not rol:
            await ctx.send("❌ Usa: `!rol @rol`")
            return

        # Count members with this role
        members_with_role = len([m for m in ctx.guild.members if rol in m.roles]) if ctx.guild.members else 0

        embed = discord.Embed(
            title=f"🎭 Rol: {rol.name}",
            color=rol.color if rol.color.value else discord.Color.default()
        )
        embed.add_field(name="🆔 ID", value=f"`{rol.id}`", inline=True)
        embed.add_field(name="👥 Miembros", value=str(members_with_role), inline=True)
        embed.add_field(name="🎨 Color", value=f"`#{rol.color.value:06X}`" if rol.color.value else "Ninguno", inline=True)
        embed.add_field(name="📌 Posición", value=str(rol.position), inline=True)
        embed.add_field(name="🔊 Mencionable", value="Sí" if rol.mentionable else "No", inline=True)
        embed.add_field(name="👁️ Visible", value="Sí" if rol.hoist else "No", inline=True)
        embed.add_field(name="📅 Creado", value=rol.created_at.strftime("%d/%m/%Y"), inline=True)

        await ctx.send(embed=embed)


    # ── Help ─────────────────────────────────────────────────────────────────
    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context) -> None:
        """Show the full command panel with all categories."""
        es_admin = ctx.author.id == ADMIN_ID
        embed = discord.Embed(
            title="🥖 Teto — Panel de Comandos",
            description=(
                "Prefijo: `cx!` — Usa `cx!help` siempre que quieras verlo.\n"
                "Los alias aparecen entre paréntesis. "
                "**`@u` = usuario opcional**."
            ),
            color=discord.Color.from_rgb(255, 105, 180),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(
            name="🎮 Diversión",
            value=(
                "`aura` [@u] — Aura diaria (resetea cada 24h)\n"
                "`top` (`ranking`, `leaderboard`) — Top 10 de aura\n"
                "`chat` (`conversar`) — Habla con Teto (IA)\n"
                "`de` (`dominio`) — Expansión de Dominio 🏮\n"
                "`bf` (`blackflash`) — Black Flash (5% duplica aura)\n"
                "`castigo` (`cast`) — Castigo aleatorio\n"
                "`alaba` (`glaze`, `alabanza`, `cumplido`) — Teto alaba 👑\n"
                "`picha` (`pp`) — Medición científica\n"
                "`ship` [@u1] [@u2] — Compatibilidad amorosa 💘\n"
                "`vs` (`versus`) — Combate 🥊\n"
                "`8ball` (`pregunta`, `ball`) — Bola 8 mística 🎱\n"
                "`elegir` — Elige entre opciones\n"
                "`hola` (`hello`, `hi`) — Saludo con GIF"
            ),
            inline=False,
        )
        embed.add_field(
            name="🛠️ Utilidad",
            value=(
                "`help` — Este panel • `ping` — Latencia\n"
                "`uptime` — Tiempo activa • `avatar` (`av`) — Foto de perfil\n"
                "`userinfo` (`user`, `u`, `info`) [@u] — Info de usuario\n"
                "`hora` — Reloj mundial • `servidor` (`server`, `serverinfo`, `guild`, `guildinfo`) — Info server\n"
                "`rol` (`role`, `roleinfo`, `rolinfo`) — Info de rol\n"
                "`recordar` (`rem`, `reminder`) — Recordatorio"
            ),
            inline=False,
        )
        embed.add_field(
            name="🌐 APIs y búsquedas",
            value=(
                "`pokemon` (`poke`, `pokedex`) — Info de Pokémon 🔍\n"
                "`pais` (`country`, `paises`) — Info de un país 🌍\n"
                "`clima` (`weather`, `tiempo`) — Clima de una ciudad 🌤️\n"
                "`anime` (`mal`, `myanimelist`) — Buscar anime en MAL 🎬\n"
                "`perro` (`dog`, `doggo`, `perrito`) — Perrito aleatorio 🐕\n"
                "`razas` (`breeds`) — Lista de razas 🐕\n"
                "`coctel` (`cocktail`, `drink`) — Receta de coctel 🍸\n"
                "`coctelaleatorio` (`randomdrink`, `randomcoctel`) — Coctel aleatorio 🍸\n"
                "`espacio` (`space`, `nasa`, `apod`) — Foto NASA del día 🚀\n"
                "`chiste` (`joke`, `chistes`) — Chiste aleatorio en español 😂\n"
                "`traducir` (`translate`, `trad`) — Traducir texto 🌐\n"
                "`receta` (`recipe`, `comida`) — Receta de comida 🍳\n"
                "`catfact` (`gatofact`, `factcat`) — Dato curioso de gatos 🐱\n"
                "`definir` (`define`, `dict`) — Definición de una palabra 📖\n"
                "`teto` — 🥖"
            ),
            inline=False,
        )
        embed.add_field(
            name="🛡️ Moderación",
            value=(
                "`purge` [N|all] — Limpiar mensajes (gestionar mensajes)\n"
                "`ruleta` (`ruleta_rusa`) — Kick aleatorio de voz (cooldown 1h)\n"
                "`angelguard` — Quita todos los timeouts ✨"
            ),
            inline=False,
        )

        if es_admin:
            embed.add_field(
                name="👑 Admin (solo tú)",
                value=(
                    "`muteall` / `unmuteall` — Silenciar/Dessilenciar canal de voz\n"
                    "`setaura` [@u] [valor] — Fijar aura · `resetaura` [@u] — Reset\n"
                    "`giveaura` (`daraura`, `regalaraura`) [N] — Dar/quitar aura\n"
                    "`decir` (`say`) — Teto habla por ti en el canal\n"
                    "`dm` (`md`, `mensajedirecto`) @u <texto> — MD a un usuario\n"
                    "`anuncio` (`announce`, `avisar`) — Anuncio oficial\n"
                    "`backup` (`exportar`, `respaldar`) — Exportar datos\n"
                    "`stats` (`botinfo`) — Dashboard del bot 📊\n"
                    "`reload` (`recargar`) [cog] — Recargar cogs 🔄\n"
                    "`logs` (`log`) [N] — Últimas líneas de log 📋\n"
                    "`blacklist` (`bl`) / `unblacklist` (`unbl`) — Bloquear usuario\n"
                    "`blacklistlist` (`bllist`) — Ver bloqueados 🚫\n"
                    "`maintenance` (`mantenimiento`) — Modo mantenimiento ⚙️\n"
                    "`maintenance_status` (`mantstatus`) — Estado mantenimiento\n"
                    "`slowmode` (`sm`) #canal [N] — Slowmode 🐌\n"
                    "`vckick` (`vcsoftban`) [@u] — Voice ban toggle (auto-kick en llamada)\n"
                    "`teamo` — 💕 (secreto)"
                ),
                inline=False,
            )
        else:
            embed.add_field(
                name="🔒 Comandos ocultos",
                value=(
                    "Hay comandos de admin que solo el dueño del bot puede usar. "
                    "Si se rompe algo, habla con él. 🥖"
                ),
                inline=False,
            )

        embed.set_footer(text="🥖 Teto aprueba este bot.")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Load the Utilidad cog."""
    await bot.add_cog(Utilidad(bot))
