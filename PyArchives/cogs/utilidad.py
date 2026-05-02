import discord
from discord.ext import commands
import random
import pytz
import time
from datetime import datetime

ADMIN_ID = 979869404110159912


class Utilidad(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command(name="ping")
    async def ping(self, ctx):
        start = time.time()
        msg = await ctx.send("🏓 Poneando...")
        await msg.edit(content=(
            f"**¡Pong!** 🏓\n"
            f"**Latencia API:** `{round(self.bot.latency * 1000)}ms`\n"
            f"**Respuesta Web:** `{round((time.time() - start) * 1000)}ms`"
        ))

    @commands.command(name="8ball", aliases=["pregunta", "ball"])
    async def eight_ball(self, ctx, *, pregunta: str):
        respuestas = [
            "Claramente sí. ✅", "Es decididamente así. ✨", "Sin ninguna duda. 💎",
            "Pregunta en otro momento... ⏳", "Mejor no te lo digo ahora. 🤐",
            "Mis fuentes dicen que no. ❌", "Las perspectivas no son buenas. 📉",
            "Muy dudoso. 🤔", "¡Por supuesto! 🚀", "No cuentes con ello. 🛑",
        ]
        embed = discord.Embed(title="🎱 La Bola 8 Mística", color=discord.Color.dark_blue())
        embed.add_field(name="Pregunta:", value=f"*{pregunta}*", inline=False)
        embed.add_field(name="Respuesta:", value=f"**{random.choice(respuestas)}**", inline=False)
        embed.set_footer(text=f"Solicitado por {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def elegir(self, ctx, *, opciones: str):
        lista = opciones.split(",")
        if len(lista) < 2:
            return await ctx.send("Pon al menos dos opciones separadas por coma. Ej: `cx!elegir pizza, hamburguesa`.")
        await ctx.send(f"🤔 Después de mucho pensar, elijo: **{random.choice(lista).strip()}**")

    @commands.command(name="avatar", aliases=["av"])
    async def avatar(self, ctx, miembro: discord.Member = None):
        miembro = miembro or ctx.author
        embed = discord.Embed(title=f"🖼️ Avatar de {miembro.name}", color=miembro.color)
        embed.set_image(url=miembro.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["user", "info", "u"])
    async def userinfo(self, ctx, miembro: discord.Member = None):
        miembro = miembro or ctx.author
        ts_creacion = int(miembro.created_at.timestamp())
        ts_union = int(miembro.joined_at.timestamp())
        roles = [r.mention for r in miembro.roles if r.name != "@everyone"]
        embed = discord.Embed(title=f"Información de {miembro.name}", color=miembro.color)
        embed.set_thumbnail(url=miembro.display_avatar.url)
        embed.add_field(name="🆔 ID", value=f"`{miembro.id}`", inline=True)
        embed.add_field(name="🏷️ Apodo", value=miembro.display_name, inline=True)
        embed.add_field(name="🗓️ Cuenta creada", value=f"<t:{ts_creacion}:D> (<t:{ts_creacion}:R>)", inline=True)
        embed.add_field(name="📥 Se unió", value=f"<t:{ts_union}:D> (<t:{ts_union}:R>)", inline=True)
        embed.add_field(name="🎭 Roles", value=" ".join(roles) if roles else "Sin roles", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["azar", "random_user"])
    async def aleatorio(self, ctx):
        usuarios = [m for m in ctx.guild.members if not m.bot]
        if not usuarios:
            return await ctx.send("No hay usuarios válidos.")
        elegido = random.choice(usuarios)
        embed = discord.Embed(title="🎲 Usuario Seleccionado", description=elegido.mention, color=discord.Color.gold())
        embed.set_thumbnail(url=elegido.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="cita")
    async def cita(self, ctx, m1_id: str, m2_id: str):
        if ctx.author.id != ADMIN_ID:
            return
        canal_destino = self.bot.get_channel(1478182165966753843)
        if not canal_destino:
            return await ctx.send("❌ No encuentro el canal de voz.")
        exitos, fallidos = [], []
        for raw_id in [m1_id, m2_id]:
            clean = "".join(filter(str.isdigit, raw_id))
            if not clean:
                fallidos.append(f"ID inválida ({raw_id})")
                continue
            miembro = None
            for guild in self.bot.guilds:
                miembro = guild.get_member(int(clean))
                if miembro:
                    break
            if miembro and miembro.voice:
                try:
                    await miembro.move_to(canal_destino)
                    exitos.append(miembro.display_name)
                except Exception:
                    fallidos.append(f"{miembro.display_name} (Error)")
            else:
                fallidos.append(f"{raw_id} (No en voz)")
        await ctx.send(f"✅ {', '.join(exitos) or 'Ninguno'} | ❌ {', '.join(fallidos) or 'Ninguno'}")

    @commands.command()
    async def hora(self, ctx):
        tzs = {"🇪🇸 Madrid": "Europe/Madrid", "🇯🇵 Japón": "Asia/Tokyo", "🇺🇸 NY": "America/New_York"}
        embed = discord.Embed(title="⌚ Reloj Mundial", color=discord.Color.blue())
        for nombre, zona in tzs.items():
            h = datetime.now(pytz.timezone(zona)).strftime("%H:%M")
            embed.add_field(name=nombre, value=f"**{h}**", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def ship(self, ctx, usuario1: discord.Member, usuario2: discord.Member = None):
        usuario2 = usuario2 or ctx.author
        if usuario2 == usuario1:
            usuario2 = ctx.author
        porcentaje = random.randint(0, 100)
        barra = "❤️" * (porcentaje // 10) + "🖤" * (10 - porcentaje // 10)
        embed = discord.Embed(title="💘 Calculadora de Amor", color=discord.Color.red())
        embed.add_field(name="Pareja", value=f"{usuario1.mention} & {usuario2.mention}", inline=False)
        embed.add_field(name="Compatibilidad", value=f"{porcentaje}%\n{barra}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        diff = int(round(time.time() - self.start_time))
        m, s = divmod(diff, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        await ctx.send(f"🕒 **Uptime:** `{d}d {h}h {m}m {s}s`")

    @commands.command(name="teto")
    async def teto(self, ctx):
        await ctx.send("**🥖 ¡Teto, yay!**\nhttps://cdn.discordapp.com/attachments/874124605533614090/1478366865201037353/pFw1Rzg.mp4?ex=69a823ef&is=69a6d26f&hm=b3570129c1ff22374ed5fff3f9a4a689128ea701408ad0a963b92d164f08ccff&")

    # --- REUNIÓN (solo admin) ---
    @commands.command(name="re", aliases=["reunion", "raid"])
    async def reunion(self, ctx, canal_destino: discord.VoiceChannel = None):
        """[Admin] Mueve a todos los que están en voz al canal indicado."""
        if ctx.author.id != ADMIN_ID:
            return
        if canal_destino is None:
            return await ctx.send("❌ Indica el canal de voz destino. Ej: `cx!re #general`")

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
                except Exception:
                    fallidos += 1

        await ctx.send(
            f"✅ Reunión completada en {canal_destino.mention}. "
            f"**{movidos}** movidos" + (f", {fallidos} fallidos." if fallidos else ".")
        )

    # --- SILENCIAR TODOS (solo admin) ---
    @commands.command(name="muteall")
    async def mute_all(self, ctx):
        """[Admin] Silencia el micro a todos en el canal de voz del admin."""
        if ctx.author.id != ADMIN_ID:
            return
        if not ctx.author.voice:
            return await ctx.send("❌ Entra en un canal de voz primero.")
        count = 0
        for miembro in ctx.author.voice.channel.members:
            if miembro.bot or miembro.id == ADMIN_ID:
                continue
            try:
                await miembro.edit(mute=True)
                count += 1
            except Exception:
                pass
        await ctx.send(f"🔇 {count} usuarios silenciados.")

    @commands.command(name="unmuteall")
    async def unmute_all(self, ctx):
        """[Admin] Quita el silencio a todos en el canal de voz del admin."""
        if ctx.author.id != ADMIN_ID:
            return
        if not ctx.author.voice:
            return await ctx.send("❌ Entra en un canal de voz primero.")
        count = 0
        for miembro in ctx.author.voice.channel.members:
            if miembro.bot:
                continue
            try:
                await miembro.edit(mute=False)
                count += 1
            except Exception:
                pass
        await ctx.send(f"🔊 {count} usuarios dessilenciados.")

    # --- HELP ---
    @commands.command(name="help")
    async def help_command(self, ctx):
        es_admin = ctx.author.id == ADMIN_ID
        embed = discord.Embed(
            title="🥖 Teto — Panel de Comandos",
            description="Prefijo: `cx!` — Todos los comandos listos para usar.",
            color=discord.Color.from_rgb(255, 105, 180)
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(
            name="🎭 Jujutsu Kaisen",
            value="`de` `bf` — Expansión de Dominio y Black Flash *(5% de duplicar aura)*",
            inline=False
        )
        embed.add_field(
            name="✨ Sistema de Aura",
            value="`aura` — Consulta tu aura diaria\n`top` `ranking` — Top 10 del server\n`da` `dueloaura` — Duelo aleatorio (+50/-100)\n`robar` `rob` — Roba aura con 50% de éxito\n`vc` `votochopped` — 3 votos = timeout 5 min",
            inline=False
        )
        embed.add_field(
            name="🔮 Diversión",
            value="`picha` `pp` — Medición científica diaria\n`8ball` `ball` — La bola 8 mística\n`ship` — Compatibilidad entre dos usuarios\n`castigo` `cast` — Sentencia aleatoria\n`vs` `versus` — Combate entre dos usuarios\n`dado` `d` — Lanza un dado (d6 por defecto)\n`elegir` — Elige entre opciones\n`aleatorio` — Usuario aleatorio del server",
            inline=False
        )
        embed.add_field(
            name="🖼️ Utilidad",
            value="`ping` — Latencia\n`avatar` `av` — Foto de perfil\n`userinfo` `u` — Info de usuario\n`hora` — Reloj mundial\n`uptime` — Tiempo activo\n`recordar` `rem` — Recordatorio *(ej: `cx!recordar 10m texto`)*\n`teto` — 🥖",
            inline=False
        )
        embed.add_field(
            name="🛡️ Moderación",
            value="`mlshr` — Purge de mensajes\n`ruleta` — Kick aleatorio de voz\n`angelguard` — Quita todos los timeouts\n`nxc` — Toggle imán de citas\n`oa` — Orden de alejamiento",
            inline=False
        )

        if es_admin:
            embed.add_field(
                name="👑 Admin (solo tú)",
                value="`re` `reunion` — Reunir toda la voz\n`muteall` `unmuteall` — Silenciar/Dessilenciar canal\n`cita` — Mover dos usuarios al canal de citas\n`setaura` `resetaura` — Control manual de aura",
                inline=False
            )

        embed.set_footer(text="🥖 Teto aprueba este bot.")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utilidad(bot))
