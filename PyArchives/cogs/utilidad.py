import discord
from discord.ext import commands
import random
import pytz
import time
from datetime import datetime
from comandos_gifs import get_giphy_gif

class Utilidad(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Muestra la latencia del bot y del sistema."""
        start_time = time.time()
        message = await ctx.send("🏓 Poneando...")
        end_time = time.time()

        bot_latency = round(self.bot.latency * 1000)
        api_latency = round((end_time - start_time) * 1000)

        await message.edit(content=f"**¡Pong!** 🏓\n**Latencia API:** `{bot_latency}ms`\n**Respuesta Web:** `{api_latency}ms`")

    @commands.command(name="8ball", aliases=['pregunta'])
    async def eight_ball(self, ctx, *, pregunta: str):
        """Responde a una pregunta con el poder de la bola 8."""
        respuestas = [
            "Claramente sí. ✅", "Es decididamente así. ✨", "Sin ninguna duda. 💎",
            "Pregunta en otro momento... ⏳", "Mejor no te lo digo ahora. 🤐",
            "Mis fuentes dicen que no. ❌", "Las perspectivas no son muy buenas. 📉",
            "Muy dudoso. 🤔", "¡Por supuesto! 🚀", "No cuentes con ello. 🛑"
        ]
        respuesta = random.choice(respuestas)
        
        embed = discord.Embed(title="🎱 La Bola 8 Mística", color=discord.Color.dark_blue())
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
        """Mueve a dos miembros al canal de citas."""
        TU_ID = 979869404110159912
        ID_CANAL_VOZ = 1478182165966753843 

        if ctx.author.id != TU_ID: return 

        canal_destino = self.bot.get_channel(ID_CANAL_VOZ)
        if not canal_destino:
            return await ctx.send("❌ No encuentro el canal de voz.")

        exitos, fallidos = [], []
        for raw_id in [m1_id, m2_id]:
            clean_id_str = "".join(filter(str.isdigit, raw_id))
            if not clean_id_str:
                fallidos.append(f"ID inválida ({raw_id})")
                continue
            
            miembro = None
            for guild in self.bot.guilds:
                miembro = guild.get_member(int(clean_id_str))
                if miembro: break
            
            if miembro and miembro.voice:
                try:
                    await miembro.move_to(canal_destino)
                    exitos.append(miembro.display_name)
                except:
                    fallidos.append(f"{miembro.display_name} (Error)")
            else:
                fallidos.append(f"{raw_id} (No en voz/encontrado)")

        await ctx.send(f"✅ {', '.join(exitos)} | ❌ {', '.join(fallidos)}")
        
    @commands.command()
    async def hora(self, ctx):
        """Reloj mundial"""
        tzs = {"🇪🇸 Madrid": "Europe/Madrid", "🇯🇵 Japón": "Asia/Tokyo", "🇺🇸 NY": "America/New_York"}
        embed = discord.Embed(title="⌚ Reloj Mundial", color=discord.Color.blue())
        for nombre, zona in tzs.items():
            h = datetime.now(pytz.timezone(zona)).strftime("%H:%M")
            embed.add_field(name=nombre, value=f"**{h}**", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def ship(self, ctx, usuario1: discord.Member, usuario2: discord.Member = None):
        """Mide la compatibilidad entre dos usuarios."""
        usuario2 = usuario2 or usuario1
        if usuario2 == usuario1: usuario1 = ctx.author

        porcentaje = random.randint(0, 100)
        barra = "❤️" * (porcentaje // 10) + "🖤" * (10 - (porcentaje // 10))
        embed = discord.Embed(title="💘 Calculadora de Amor", color=discord.Color.red())
        embed.add_field(name="Pareja", value=f"{usuario1.mention} & {usuario2.mention}", inline=False)
        embed.add_field(name="Compatibilidad", value=f"{porcentaje}% \n{barra}", inline=False)
        await ctx.send(embed=embed)
        
    @commands.command(name="teto")
    async def teto(self, ctx):
        """Envía el video místico de Kasane Teto."""
        video_url = "https://cdn.discordapp.com/attachments/874124605533614090/1478366865201037353/pFw1Rzg.mp4?ex=69a823ef&is=69a6d26f&hm=b3570129c1ff22374ed5fff3f9a4a689128ea701408ad0a963b92d164f08ccff&"
        
        # Enviamos el mensaje con el video. Discord lo reproducirá automáticamente.
        await ctx.send(f"**🥖 ¡Teto Territorial!**\n{video_url}")

    @commands.command(name="help")
    async def help_command(self, ctx):
        """Muestra la lista completa de comandos disponibles."""
        embed = discord.Embed(
            title="🏮 Panel de Control - Sukuna's Vessel",
            description="El prefijo es `cx!`",
            color=discord.Color.gold()
        )
        embed.add_field(name="🎭 Jujutsu Kaisen", value="`de`, `bf`", inline=False)
        embed.add_field(name="🔮 Utilidad", value="`ping`, `avatar`, `8ball`, `ship`, `userinfo`, `hora`, `hola`, `aleatorio`, `teto`", inline=False)
        embed.add_field(name="🛡️ Moderación", value="`echo`, `cita`, `mlshr`, `ruleta`, `angelguard`", inline=False)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilidad(bot))