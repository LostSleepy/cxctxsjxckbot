import discord
import os
import aiohttp
import random

async def get_giphy_gif(query):
    """
    API Alternativa de Anime (nekos.best).
    No necesita Key y es ultra rápida.
    """
    # Mapeamos tus búsquedas a 'categorías' de la API
    # Si la búsqueda contiene estas palabras, pedimos esa categoría
    query = query.lower()
    category = "punch" # Por defecto
    
    if "hello" in query or "hola" in query:
        category = "wave"
    elif "domain" in query or "special" in query:
        category = "glance"
    elif "black flash" in query:
        category = "punch"
    else:
        # Si no encaja, pedimos una categoría aleatoria de acción
        category = random.choice(["smile", "pout", "think", "bored"])

    url = f"https://nekos.best/api/v2/{category}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    # La estructura de nekos.best es: {"results": [{"url": "..."}]}
                    return data['results'][0]['url']
        except Exception as e:
            print(f"❌ Error en API de respaldo: {e}")
    
    # Si internet se cae, este es el GIF de emergencia (Itadori)
    return "https://media.tenor.com/26_v9S66_B4AAAAC/itadori-yuuji-jujutsu-kaisen.gif"

# --- Comandos ---

async def bf(ctx, usuario: discord.Member = None):
    if usuario is None: return await ctx.send("Menciona a alguien para darle el Black Flash.")
    async with ctx.typing():
        gif = await get_giphy_gif("black flash")
        embed = discord.Embed(title="⚡¡Black Flash!⚡", description=f"{ctx.author.mention} le ha hecho un **Black Flash** a {usuario.mention}.", color=discord.Color.red())
        embed.set_image(url=gif)
        await ctx.send(embed=embed)

async def de(ctx, usuario: discord.Member = None):
    if usuario is None: return await ctx.send("Menciona a alguien para encerrarlo en tu dominio.")
    async with ctx.typing():
        gif = await get_giphy_gif("domain expansion")
        embed = discord.Embed(title="¡EXPANSION DE DOMINIO!", description=f"{ctx.author.mention} ha atrapado a {usuario.mention} en su dominio.", color=discord.Color.blue())
        embed.set_image(url=gif)
        await ctx.send(embed=embed)