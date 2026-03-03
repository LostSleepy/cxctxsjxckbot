import discord
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()
GIPHY_API_KEY = os.getenv('GIPHY_KEY')

async def get_giphy_gif(query):
    if not GIPHY_API_KEY:
        print("DEBUG: No se encontró GIPHY_KEY en el .env")
        return None

    # Usamos el endpoint de búsqueda (search) para mayor precisión en JJK
    url = "https://api.giphy.com/v1/gifs/search"
    params = {
        'api_key': GIPHY_API_KEY,
        'q': query,
        'limit': 20,
        'rating': 'pg-13'
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('data', [])
                    if results:
                        # Seleccionamos un GIF aleatorio de los primeros 20 resultados
                        import random
                        return random.choice(results)['images']['original']['url']
                else:
                    print(f"DEBUG: Error Giphy Status {response.status}")
        except Exception as e:
            print(f"DEBUG: Error de conexión: {e}")
    return None

async def bf(ctx, usuario: discord.Member = None):
    if usuario is None:
        return await ctx.send("Debes mencionar a un usuario.")

    async with ctx.typing():
        gif = await get_giphy_gif("itadori black flash")
        
        embed = discord.Embed(
            title="⚡¡Black Flash!⚡",
            description=f"{ctx.author.mention} le ha hecho un **Black Flash** a {usuario.mention}.",
            color=discord.Color.red()
        )
        if gif: embed.set_image(url=gif)
        await ctx.send(embed=embed)

async def de(ctx, usuario: discord.Member = None):
    if usuario is None:
        return await ctx.send("Debes mencionar a un usuario.")

    async with ctx.typing():
        gif = await get_giphy_gif("jujutsu kaisen domain expansion")
        
        embed = discord.Embed(
            title="¡EXPANSION DE DOMINIO!",
            description=f"{ctx.author.mention} le ha expandido su **dominio** a {usuario.mention}",
            color=discord.Color.blue()
        )
        if gif: embed.set_image(url=gif)
        await ctx.send(embed=embed)