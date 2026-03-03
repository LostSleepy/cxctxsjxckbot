import discord
import os
import aiohttp
import random
from dotenv import load_dotenv

load_dotenv()

# Cambiamos la variable a la nueva de Klipy
KLIPY_API_KEY = os.getenv('KLIPY_KEY')

async def get_giphy_gif(query):
    """
    Obtiene un GIF de Klipy. 
    Mantenemos el nombre de la función para no romper tus otros archivos.
    """
    if not KLIPY_API_KEY:
        print("DEBUG: No se encontró KLIPY_KEY en las variables de entorno")
        return None

    # Endpoint de búsqueda de Klipy
    url = "https://api.klipy.com/v1/gifs/search"
    params = {
        'api_key': KLIPY_API_KEY,
        'q': query,
        'limit': 20
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('data', [])
                    if results:
                        # Seleccionamos un GIF aleatorio
                        gif_obj = random.choice(results)
                        # Estructura de Klipy: images -> original -> url
                        return gif_obj.get('images', {}).get('original', {}).get('url')
                else:
                    print(f"DEBUG: Error Klipy Status {response.status}")
        except Exception as e:
            print(f"DEBUG: Error de conexión con Klipy: {e}")
    return None

async def bf(ctx, usuario: discord.Member = None):
    if usuario is None:
        return await ctx.send("Debes mencionar a un usuario.")

    async with ctx.typing():
        # Búsqueda específica en Klipy
        gif = await get_giphy_gif("itadori black flash")
        
        embed = discord.Embed(
            title="⚡¡Black Flash!⚡",
            description=f"{ctx.author.mention} le ha hecho un **Black Flash** a {usuario.mention}.",
            color=discord.Color.red()
        )
        if gif: 
            embed.set_image(url=gif)
        else:
            embed.set_footer(text="No se pudo cargar el GIF de Klipy")
            
        await ctx.send(embed=embed)

async def de(ctx, usuario: discord.Member = None):
    if usuario is None:
        return await ctx.send("Debes mencionar a un usuario.")

    async with ctx.typing():
        # Búsqueda específica en Klipy
        gif = await get_giphy_gif("jujutsu kaisen domain expansion")
        
        embed = discord.Embed(
            title="¡EXPANSION DE DOMINIO!",
            description=f"{ctx.author.mention} le ha expandido su **dominio** a {usuario.mention}",
            color=discord.Color.blue()
        )
        if gif: 
            embed.set_image(url=gif)
        else:
            embed.set_footer(text="No se pudo cargar el GIF de Klipy")
            
        await ctx.send(embed=embed)