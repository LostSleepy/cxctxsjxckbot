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
        """Show detailed user information."""
        miembro = miembro or ctx.author
        created_ts = int(miembro.created_at.timestamp())
        joined_ts = int(miembro.joined_at.timestamp())
        roles = [r.mention for r in miembro.roles if r.name != "@everyone"]

        embed = discord.Embed(
            title=f"Información de {miembro.name}",
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
        """Show the command panel."""
        es_admin = ctx.author.id == ADMIN_ID
        embed = discord.Embed(
            title="🥖 Teto — Panel de Comandos",
            description="Prefijo: `cx!` — Todos los comandos listos para usar.",
            color=discord.Color.from_rgb(255, 105, 180),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(
            name="🎮 Diversión",
            value=(
                "`aura` — Aura diaria • `top` — Ranking de aura\n"
                "`vc` `votochopped` — Vota para timeout\n"
                "`chat` `conversar` — Habla con Teto\n"
                "`de` — Expansión de Dominio • `bf` — Black Flash\n"
                "`choppeddaily` `cd` — Chopped diario 🥖\n"
                "`castigo` `cast` — Castigo aleatorio\n"
                "`alaba` `glaze` — Teto alaba 👑\n"
                "`picha` `pp` — Medición científica\n"
                "`ship` — Compatibilidad amorosa 💘\n"
                "`vs` `versus` — Combate • `8ball` — Bola mística\n"
                "`elegir` — Elige entre opciones\n"
                "`hola` `hello` — Saludo con GIF"
            ),
            inline=False,
        )
        embed.add_field(
            name="🛠️ Utilidad",
            value=(
                "`ping` — Latencia • `uptime` — Tiempo activo\n"
                "`avatar` `av` — Foto de perfil\n"
                "`userinfo` `u` — Info de usuario\n"
                "`hora` — Reloj mundial • `servidor` — Info server\n"
                "`rol` `role` — Info de rol\n"
                "`recordar` `rem` — Recordatorio\n"
                "`pokemon` `poke` — Info de Pokémon 🔍\n"
                "`teto` — 🥖"
            ),
            inline=False,
        )
        embed.add_field(
            name="🛡️ Moderación",
            value=(
                "`purge` — Limpiar mensajes\n"
                "`ruleta` — Kick aleatorio de voz\n"
                "`angelguard` — Quita todos los timeouts"
            ),
            inline=False,
        )

        if es_admin:
            embed.add_field(
                name="👑 Admin (solo tú)",
                value=(
                    "`muteall` `unmuteall` — Silenciar/Dessilenciar canal\n"
                    "`setaura` `resetaura` — Control manual de aura\n"
                    "`giveaura` `daraura` — Dar o quitar aura a alguien\n"
                    "`decir` `say` — Teto habla por ti\n"
                    "`dm` `md` — Enviar MD a un usuario\n"
                    "`anuncio` `announce` — Anuncio oficial\n"
                    "`backup` `exportar` — Exportar datos del bot\n"
                    "`teamo` — 💕 (secreto)"
                ),
                inline=False,
            )

        embed.set_footer(text="🥖 Teto aprueba este bot.")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Load the Utilidad cog."""
    await bot.add_cog(Utilidad(bot))
