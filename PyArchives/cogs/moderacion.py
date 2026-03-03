import discord
from discord.ext import commands
import random
from datetime import timedelta

class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ruleta', 'mute_random'])
    @commands.has_permissions(moderate_members=True)
    async def ruleta_rusa(self, ctx):
        """Selecciona a alguien al azar y le aplica un timeout de 10 minutos."""
        # Filtramos: No bots, no el autor del comando, y solo gente que el bot puede mutear
        usuarios = [
            m for m in ctx.guild.members 
            if not m.bot and m.id != ctx.author.id and m.top_role < ctx.guild.me.top_role
        ]
        
        if not usuarios:
            return await ctx.send("❌ No hay usuarios válidos en mi rango de alcance para jugar.")

        elegido = random.choice(usuarios)
        tiempo = timedelta(minutes=10)

        try:
            await elegido.timeout(tiempo, reason=f"Perdió en la ruleta rusa iniciada por {ctx.author}")
            
            embed = discord.Embed(
                title="🎲 Ruleta Rusa de Silencio",
                description=f"La suerte ha decidido que... {elegido.mention} sea silenciado.\n\n⏱️ **Duración:** 10 minutos.",
                color=discord.Color.red()
            )
            embed.set_footer(text="¡Usa !angelguard para salvarlo!")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"⚠️ Error al intentar silenciar a {elegido.name}: {e}")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def angelguard(self, ctx):
        """Quita el timeout a todos los usuarios silenciados del servidor."""
        count = 0
        status_msg = await ctx.send("😇 **Buscando almas silenciadas para liberar...**")

        for miembro in ctx.guild.members:
            if miembro.timed_out_until is not None:
                try:
                    await miembro.edit(timed_out_until=None, reason=f"Liberado por AngelGuard de {ctx.author}")
                    count += 1
                except:
                    pass

        if count > 0:
            embed = discord.Embed(
                title="✨ AngelGuard Activo",
                description=f"Se ha restaurado el equilibrio.\nHe devuelto la voz a **{count}** usuario(s).",
                color=discord.Color.gold()
            )
            await status_msg.edit(content=None, embed=embed)
        else:
            await status_msg.edit(content="🙏 No hay nadie silenciado actualmente.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def mlshr(self, ctx, amount: str):
        """Borra mensajes del chat."""
        if amount.lower() == 'all':
            await ctx.channel.purge()
            await ctx.send('✅ Chat purificado correctamente.', delete_after=5)
        else:
            try:
                num = int(amount)
                await ctx.channel.purge(limit=num)
                await ctx.send(f'✅ Se han borrado {num} mensajes.', delete_after=5)
            except:
                await ctx.send('❌ Indica un número o "all".', delete_after=5)

async def setup(bot):
    await bot.add_cog(Moderacion(bot))