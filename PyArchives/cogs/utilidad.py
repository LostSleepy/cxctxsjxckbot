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


    # ── Emoji ────────────────────────────────────────────────────────────────
    @commands.command(name="emoji", aliases=["agrandar", "jumbo", "emojigrande"])
    async def emoji_info(self, ctx: commands.Context, *, nombre_emoji: str = None) -> None:
        """Muestra un emoji personalizado del servidor en grande."""
        if not nombre_emoji:
            await ctx.send("❌ Usa: `!emoji <nombre>`")
            return

        nombre_emoji = nombre_emoji.strip().strip(':')

        # Search through guild emojis
        found = None
        for emoji in ctx.guild.emojis:
            if emoji.name.lower() == nombre_emoji.lower():
                found = emoji
                break

        if not found:
            await ctx.send(f"❌ No encontré un emoji llamado `{nombre_emoji}` en este servidor.")
            return

        embed = discord.Embed(
            title=f":{found.name}:",
            description=f"🔗 **Link:** [Click aquí]({found.url})\n"
                        f"🆔 **ID:** `{found.id}`\n"
                        f"{'🎞️ **Animado**' if found.animated else '🖼️ **Estático**'}",
            color=discord.Color.gold()
        )
        embed.set_image(url=found.url)
        await ctx.send(embed=embed)


    # ── Encuesta ─────────────────────────────────────────────────────────────
    @commands.command(name="encuesta", aliases=["votacion", "poll"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def encuesta(self, ctx: commands.Context, *, pregunta: str = None) -> None:
        """Crea una encuesta con reacciones ✅/❌."""
        await self._bypass_cooldown(ctx)
        if not pregunta:
            await ctx.send("❌ Usa: `!encuesta <pregunta>`")
            return

        embed = discord.Embed(
            title="📊 Encuesta",
            description=pregunta,
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"Propuesta por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")


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
                "`de` `bf` — Expansión de Dominio y Black Flash\n"
                "`ritual` — Ritual misterioso con efectos de aura\n"
                "`maldicion` — Maldice a alguien (JJK style)\n"
                "`dedo` `buscardedo` — Busca un dedo de Sukuna \n"
                "`sukuna` `dedos` — Tus dedos de Sukuna recolectados"
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
                "`vc` `votochopped` — 3 votos = timeout 5 min\n"
                "`tienda` `shop` — Compra objetos con aura\n"
                "`comprar` `buy` — Adquiere un objeto de la tienda\n"
                "`inventario` `inv` — Tus objetos comprados"
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
                "`aleatorio` — Usuario aleatorio del server\n"
                "`ppt` `piedra` — Piedra, Papel o Tijera vs Teto\n"
                "`coinflip` `tirar` — Cara o cruz\n"
                "`insultar` — Insulta a alguien con estilo\n"
                "`felicitar` — Felicita a un usuario\n"
                "`fraude` `fraud` — Fraud scan brainrot definitivo 🔍"
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
                "`servidor` `server` — Info del servidor\n"
                "`rol` `role` — Info de un rol\n"
                "`emoji` `agrandar` — Emoji en grande\n"
                "`encuesta` `poll` — Crea una votación\n"
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
                    "`giveaura` `daraura` — Dar o quitar aura a alguien\n"
                    "`decir` `say` — Teto habla por ti\n"
                    "`saycanal` `hablar` — Teto habla en un canal\n"
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
