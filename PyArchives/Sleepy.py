import discord
from discord.ext import commands
from comandos_gifs import bf, de  # Importa las funciones desde el otro archivo
from dotenv import load_dotenv
import os

# Carga las variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configura el bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# Evento: Cuando el bot está listo
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

# Comando para borrar una cantidad específica de mensajes
@bot.command()
@commands.has_permissions(manage_messages=True)
async def mlshr(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'Se han borrado {amount} mensajes.', delete_after=5)
    @mlshr.error
    async def mlshr_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('No tienes permisos para borrar mensajes.', delete_after=5)
        elif isinstance(error, commands.BadArgument):
            await ctx.send('Por favor, proporciona un número válido de mensajes a borrar.', delete_after=5)

    @bot.command()
    @commands.has_permissions(manage_messages=True)
    async def mlshr(ctx, amount: str):
        if amount.lower() == 'all':
            await ctx.channel.purge()
            await ctx.send('Se han borrado todos los mensajes del canal.', delete_after=5)
        else:
            try:
                amount = int(amount)
                await ctx.channel.purge(limit=amount)
                await ctx.send(f'Se han borrado {amount} mensajes.', delete_after=5)
            except ValueError:
                await ctx.send('Por favor, proporciona un número válido de mensajes a borrar.', delete_after=5)

# Comandos básicos
@bot.command()
async def hola(ctx):
    await ctx.send(f'¡Hola, {ctx.author.mention}!')

@bot.command()
async def adios(ctx):
    await ctx.send('¡Adiós! ¡Que tengas un buen día!')

@bot.command()
async def hora(ctx):
    from datetime import datetime
    ahora = datetime.now()
    await ctx.send(f'Son las {ahora.strftime("%H:%M")}.')

@bot.command()
async def repetir(ctx, *, mensaje: str):
    await ctx.send(f'Has dicho: {mensaje}')
    
# Comandos con funciones en otro archivo - USANDO ALIAS
@bot.command(aliases=['de'])  # Alias 'de' para el comando 'de_command'
async def de_command(ctx, usuario: discord.Member = None):
    await de(ctx, usuario)

@bot.command(aliases=['bf'])  # Alias 'bf' para el comando 'bf_command'
async def bf_command(ctx, usuario: discord.Member = None):
    await bf(ctx, usuario)


        
# Ejecuta el bot
bot.run(TOKEN)