"""
Utility commands cog for the Teto Discord bot.
Includes ping, 8ball, avatar, userinfo, ship, uptime, hora, help, and more.
"""
import logging
import random
import time
from datetime import datetime
from typing import List, Optional

import discord
import pytz
from discord.ext import commands

from config import ADMIN_ID, CANAL_CITAS_ID

log = logging.getLogger(__name__)


class Utilidad(commands.Cog):
    """Utility and general-purpose commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._start_time: float = time.time()

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

    # ── Aleatorio ────────────────────────────────────────────────────────────
    @commands.command(name="aleatorio", aliases=["azar", "random_user"])
    async def aleatorio(self, ctx: commands.Context) -> None:
        """Pick a random server member."""
        usuarios = [m for m in ctx.guild.members if not m.bot]
        if not usuarios:
            await ctx.send("No hay usuarios válidos.")
            return
        elegido = random.choice(usuarios)
        embed = discord.Embed(
            title="🎲 Usuario Seleccionado",
            description=elegido.mention,
            color=discord.Color.gold(),
        )
        embed.set_thumbnail(url=elegido.display_avatar.url)
        await ctx.send(embed=embed)

    # ── Cita (admin only) ────────────────────────────────────────────────────
    @commands.command(name="cita")
    async def cita(
        self, ctx: commands.Context, m1_id: str, m2_id: str
    ) -> None:
        """[Admin] Move two users to the date channel."""
        if ctx.author.id != ADMIN_ID:
            return
        canal_destino = self.bot.get_channel(CANAL_CITAS_ID)
        if not canal_destino:
            await ctx.send("❌ No encuentro el canal de voz.")
            return

        exitos: List[str] = []
        fallidos: List[str] = []

        for raw_id in [m1_id, m2_id]:
            cleaned = "".join(filter(str.isdigit, raw_id))
            if not cleaned:
                fallidos.append(f"ID inválida ({raw_id})")
                continue
            miembro: Optional[discord.Member] = None
            for guild in self.bot.guilds:
                miembro = guild.get_member(int(cleaned))
                if miembro:
                    break
            if miembro and miembro.voice:
                try:
                    await miembro.move_to(canal_destino)
                    exitos.append(miembro.display_name)
                except discord.DiscordException:
                    fallidos.append(f"{miembro.display_name} (Error)")
            else:
                fallidos.append(f"{raw_id} (No en voz)")

        await ctx.send(
            f"✅ {', '.join(exitos) or 'Ninguno'} | "
            f"❌ {', '.join(fallidos) or 'Ninguno'}"
        )

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
        """Calculate love compatibility between two users."""
        usuario2 = usuario2 or ctx.author
        if usuario2 == usuario1:
            usuario2 = ctx.author

        porcentaje = random.randint(0, 100)
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

    # ── Reunión (admin only) ─────────────────────────────────────────────────
    @commands.command(name="re", aliases=["reunion", "raid"])
    async def reunion(
        self,
        ctx: commands.Context,
        canal_destino: Optional[discord.VoiceChannel] = None,
    ) -> None:
        """[Admin] Move all voice users to the specified channel."""
        if ctx.author.id != ADMIN_ID:
            return
        if canal_destino is None:
            await ctx.send("❌ Indica el canal de voz destino. Ej: `cx!re #general`")
            return

        movidos = 0
        fallidos = 0
        for canal in ctx.guild.voice_channels:
            if canal.id == canal_destino.id:
                continue
            for miembro in canal.members:
                if miembro.bot:
                    continue
                try:
                    await miembro.move_to(canal_destino)
                    movidos += 1
                except discord.DiscordException:
                    fallidos += 1

        mensaje = (
            f"✅ Reunión completada en {canal_destino.mention}. "
            f"**{movidos}** movidos"
        )
        if fallidos:
            mensaje += f", {fallidos} fallidos."
        else:
            mensaje += "."
        await ctx.send(mensaje)

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
            name="🎭 Jujutsu Kaisen",
            value=(
                "`de` `bf` — Expansión de Dominio y Black Flash "
                "*(5% de duplicar aura)*"
            ),
            inline=False,
        )
        embed.add_field(
            name="✨ Sistema de Aura",
            value=(
                "`aura` — Consulta tu aura diaria\n"
                "`top` `ranking` — Top 10 del server\n"
                "`da` `dueloaura` — Duelo aleatorio (+50/-100)\n"
                "`robar` `rob` — Roba aura con 50% de éxito\n"
                "`vc` `votochopped` — 3 votos = timeout 5 min"
            ),
            inline=False,
        )
        embed.add_field(
            name="🔮 Diversión",
            value=(
                "`alaba` `glaze` — Teto alaba a quien digas 👑\n"
                "`picha` `pp` — Medición científica diaria\n"
                "`8ball` `ball` — La bola 8 mística\n"
                "`ship` — Compatibilidad entre dos usuarios\n"
                "`castigo` `cast` — Sentencia aleatoria\n"
                "`vs` `versus` — Combate entre dos usuarios\n"
                "`dado` `d` — Lanza un dado (d6 por defecto)\n"
                "`elegir` — Elige entre opciones\n"
                "`aleatorio` — Usuario aleatorio del server"
            ),
            inline=False,
        )
        embed.add_field(
            name="🖼️ Utilidad",
            value=(
                "`ping` — Latencia\n"
                "`avatar` `av` — Foto de perfil\n"
                "`userinfo` `u` — Info de usuario\n"
                "`hora` — Reloj mundial\n"
                "`uptime` — Tiempo activo\n"
                "`recordar` `rem` — Recordatorio *(ej: `cx!recordar 10m texto`)*\n"
                "`teto` — 🥖"
            ),
            inline=False,
        )
        embed.add_field(
            name="🛡️ Moderación",
            value=(
                "`mlshr` — Purge de mensajes\n"
                "`ruleta` — Kick aleatorio de voz\n"
                "`angelguard` — Quita todos los timeouts\n"
                "`nxc` — Toggle imán de citas\n"
                "`oa` — Orden de alejamiento"
            ),
            inline=False,
        )

        if es_admin:
            embed.add_field(
                name="👑 Admin (solo tú)",
                value=(
                    "`re` `reunion` — Reunir toda la voz\n"
                    "`muteall` `unmuteall` — Silenciar/Dessilenciar canal\n"
                    "`cita` — Mover dos usuarios al canal de citas\n"
                    "`setaura` `resetaura` — Control manual de aura\n"
                    "`teamo` — 💕 (secreto)"
                ),
                inline=False,
            )

        embed.set_footer(text="🥖 Teto aprueba este bot.")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Load the Utilidad cog."""
    await bot.add_cog(Utilidad(bot))
