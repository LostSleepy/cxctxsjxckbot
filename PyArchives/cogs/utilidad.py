import discord
from discord.ext import commands
import random
import pytz
from datetime import datetime
from comandos_gifs import get_giphy_gif

class Utilidad(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="8ball", aliases=['pregunta'])
    async def eight_ball(self, ctx, *, pregunta: str):
        """Responde a una pregunta con el poder de la bola 8."""
        respuestas = [
            "Claramente sí. ✅",
            "Es decididamente así. ✨",
            "Sin ninguna duda. 💎",
            "Pregunta en otro momento... ⏳",
            "Mejor no te lo digo ahora. 🤐",
            "Mis fuentes dicen que no. ❌",
            "Las perspectivas no son muy buenas. 📉",
            "Muy dudoso. 🤔",
            "¡Por supuesto! 🚀",
            "No cuentes con ello. 🛑"
        ]
        
        respuesta = random.choice(respuestas)
        
        embed = discord.Embed(
            title="🎱 La Bola 8 Mística",
            description=f"Has consultado al destino...",
            color=discord.Color.dark_blue()
        )
        embed.add_field(name="Pregunta:", value=f"*{pregunta}*", inline=False)
        embed.add_field(name="Respuesta:", value=f"**{respuesta}**", inline=False)
        embed.set_footer(text=f"Solicitado por {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, miembro: discord.Member = None):
        """Muestra la foto de perfil de un usuario."""
        miembro = miembro or ctx.author
        embed = discord.Embed(title=f"🖼️ Avatar de {miembro.name}", color=miembro.color)
        embed.set_image(url=miembro.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['user', 'info'])
    async def userinfo(self, ctx, miembro: discord.Member = None):
        """Muestra info detallada del usuario."""
        miembro = miembro or ctx.author
        ts_creacion = int(miembro.created_at.timestamp())
        ts_union = int(miembro.joined_at.timestamp())
        roles = [role.mention for role in miembro.roles if role.name != "@everyone"]
        roles_str = " ".join(roles) if roles else "Sin roles"

        embed = discord.Embed(title=f"Información de {miembro.name}", color=miembro.color)
        embed.set_thumbnail(url=miembro.display_avatar.url)
        embed.add_field(name="🆔 ID", value=f"`{miembro.id}`", inline=True)
        embed.add_field(name="🏷️ Apodo", value=miembro.display_name, inline=True)
        embed.add_field(name="🗓️ Cuenta creada", value=f"<t:{ts_creacion}:D> (<t:{ts_creacion}:R>)", inline=True)
        embed.add_field(name="📥 Se unió", value=f"<t:{ts_union}:D> (<t:{ts_union}:R>)", inline=True)
        embed.add_field(name="🎭 Roles", value=roles_str, inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['azar', 'random_user'])
    async def aleatorio(self, ctx):
        """Selecciona un usuario aleatorio del servidor"""
        usuarios = [m for m in ctx.guild.members if not m.bot]
        if not usuarios: return await ctx.send("No hay usuarios válidos.")
        elegido = random.choice(usuarios)
        embed = discord.Embed(title="🎲 Usuario Seleccionado", description=f"{elegido.mention}", color=discord.Color.gold())
        embed.set_thumbnail(url=elegido.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def hola(self, ctx):
        """Saluda con un GIF"""
        async with ctx.typing():
            gif = await get_giphy_gif("anime hello")
            embed = discord.Embed(title=f"¡Hola, {ctx.author.name}!", color=discord.Color.purple())
            if gif: embed.set_image(url=gif)
            await ctx.send(embed=embed)
            
    @commands.command(name="cita")
    async def cita(self, ctx, m1_id: str, m2_id: str):
        """Mueve a dos miembros al canal de citas. Uso: cx!cita @m1 @m2 o cx!cita ID1 ID2"""
        TU_ID = 979869404110159912
        ID_CANAL_VOZ = 1478182165966753843 

        if ctx.author.id != TU_ID:
            return 

        canal_destino = self.bot.get_channel(ID_CANAL_VOZ)
        
        if not canal_destino:
            return await ctx.send("❌ No encuentro el canal de voz. Revisa si el bot está en ese servidor.")

        exitos = []
        fallidos = []

        for raw_id in [m1_id, m2_id]:
            clean_id_str = "".join(filter(str.isdigit, raw_id))
            if not clean_id_str:
                fallidos.append(f"ID inválida ({raw_id})")
                continue
            
            target_id = int(clean_id_str)
            miembro = None

            for guild in self.bot.guilds:
                miembro = guild.get_member(target_id)
                if miembro: break
            
            if miembro:
                if miembro.voice:
                    try:
                        await miembro.move_to(canal_destino, reason="Cita privada organizada.")
                        exitos.append(miembro.display_name)
                    except Exception as e:
                        fallidos.append(f"{miembro.display_name} (Sin permisos o error)")
                else:
                    fallidos.append(f"{miembro.display_name} (No está en voz)")
            else:
                fallidos.append(f"ID {target_id} (No encontrado)")

        msg = []
        if exitos: msg.append(f"✅ **Movidos:** {', '.join(exitos)}")
        if fallidos: msg.append(f"❌ **Fallos:** {', '.join(fallidos)}")
        
        await ctx.send("\n".join(msg) if msg else "Acción procesada.")
        
    @commands.command()
    async def hora(self, ctx):
        """Reloj mundial"""
        tzs = {"🇪🇸 Madrid": "Europe/Madrid", "🇯🇵 Japón": "Asia/Tokyo", "🇺🇸 NY": "America/New_York"}
        embed = discord.Embed(title="⌚ Reloj Mundial", color=discord.Color.blue())
        for nombre, zona in tzs.items():
            hora = datetime.now(pytz.timezone(zona)).strftime("%H:%M")
            embed.add_field(name=nombre, value=f"**{hora}**", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def repetir(self, ctx, *, mensaje: str):
        await ctx.send(mensaje)
        
    @commands.command()
    async def ship(self, ctx, usuario1: discord.Member, usuario2: discord.Member = None):
        """Mide la compatibilidad entre dos usuarios."""
        if usuario2 is None:
            usuario2 = usuario1
            usuario1 = ctx.author

        porcentaje = random.randint(0, 100)
        lleno = int(porcentaje / 10)
        vacio = 10 - lleno
        barra = "❤️" * lleno + "🖤" * vacio

        embed = discord.Embed(
            title="💘 Calculadora de Amor",
            description=f"**{usuario1.display_name}** & **{usuario2.display_name}**",
            color=discord.Color.red()
        )
        embed.add_field(name="Compatibilidad", value=f"{porcentaje}%", inline=True)
        embed.add_field(name="Análisis", value=barra, inline=False)
        
        if porcentaje > 85: frase = "¡Pareja ideal! Destinados a estar juntos. ✨"
        elif porcentaje > 50: frase = "Hay chispa, podrían intentarlo. 😉"
        else: frase = "Mejor queden como amigos... 💀"
        
        embed.set_footer(text=frase)
        await ctx.send(embed=embed)

    @commands.command(name="serverinfo", aliases=['server'])
    async def server_info(self, ctx):
        """Muestra datos detallados del servidor."""
        guild = ctx.guild
        total = guild.member_count
        humanos = len([m for m in guild.members if not m.bot])
        bots = total - humanos
        ts_creacion = int(guild.created_at.timestamp())

        embed = discord.Embed(title=f"📊 Información de {guild.name}", color=discord.Color.green())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👑 Dueño", value=guild.owner.mention, inline=True)
        embed.add_field(name="🆔 ID del Servidor", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="📅 Creado el", value=f"<t:{ts_creacion}:D>", inline=True)
        embed.add_field(name="👥 Miembros", value=f"Total: {total}\nPersonas: {humanos}\nBots: {bots}", inline=True)
        embed.add_field(name="💬 Canales", value=f"Texto: {len(guild.text_channels)}\nVoz: {len(guild.voice_channels)}", inline=True)
        embed.add_field(name="⭐ Mejoras", value=f"Nivel {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def echo(self, ctx, canal: discord.TextChannel, *, mensaje: str):
        """Envía un anuncio elegante en formato Embed a un canal específico."""
        embed = discord.Embed(
            description=mensaje,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_author(name=f"Anuncio de {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        try:
            await canal.send(embed=embed)
            await ctx.message.add_reaction("✅")
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para escribir en ese canal.")
                
    @commands.command(name="help")
    async def help_command(self, ctx):
        """Muestra la lista completa de comandos disponibles."""
        embed = discord.Embed(
            title="🏮 Panel de Control - Sukuna's Vessel",
            description="Aquí tienes la lista de comandos disponibles. El prefijo es `cx!`",
            color=discord.Color.gold()
        )

        embed.add_field(
            name="🎭 Jujutsu Kaisen",
            value="`cx!de @user` - Expansión de Dominio.\n`cx!bf @user` - Black Flash.",
            inline=False
        )

        embed.add_field(
            name="🔮 Utilidad & Diversión",
            value="`cx!avatar @user` - Avatar.\n`cx!8ball [msj]` - Bola 8.\n`cx!ship @u1 @u2` - Amor.\n`cx!serverinfo` - Info Server.\n`cx!hora` - Reloj.\n`cx!hola` - GIFs.",
            inline=False
        )

        embed.add_field(
            name="🛡️ Moderación",
            value="`cx!mlshr [N]` - Limpiar.\n`cx!echo #ch [msj]` - Anuncio.\n`cx!ruleta` - Azar.\n`cx!angelguard` - Unmute.\n`cx!cita ID1 ID2` - Citas.",
            inline=False
        )

        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed)

# Función setup fuera de la clase
async def setup(bot):
    await bot.add_cog(Utilidad(bot))