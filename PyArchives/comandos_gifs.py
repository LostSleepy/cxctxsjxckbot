import discord
import os
import aiohttp
import random
from dotenv import load_dotenv

load_dotenv()

KLIPY_API_KEY = os.getenv('KLIPY_KEY')

async def get_giphy_gif(query):
    """Obtiene un GIF de Klipy (mantenemos nombre por compatibilidad)."""
    if not KLIPY_API_KEY:
        print("❌ DEBUG: KLIPY_KEY no encontrada en variables de entorno.")
        return None

    # Endpoint oficial de búsqueda
    url = "https://api.klipy.com/v1/gifs/search"
    params = {
        'api_key': KLIPY_API_KEY,
        'q': query,
        'limit': 10
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('data', [])
                    
                    if not results:
                        print(f"⚠️ DEBUG: Klipy no encontró nada para: {query}")
                        return None

                    # Seleccionamos uno al azar
                    gif_obj = random.choice(results)
                    
                    # Intentamos obtener la URL de diferentes formas por si Klipy cambia la estructura
                    images = gif_obj.get('images', {})
                    # Priorizamos 'original', si no, buscamos 'fixed_height'
                    gif_url = images.get('original', {}).get('url') or images.get('fixed_height', {}).get('url')
                    
                    if gif_url:
                        return gif_url
                    else:
                        print(f"❌ DEBUG: Estructura de imagen no reconocida en Klipy: {gif_obj.keys()}")
                else:
                    print(f"❌ DEBUG: Error Klipy Status {response.status}. Msg: {await response.text()}")
        except Exception as e:
            print(f"❌ DEBUG: Error de conexión con Klipy: {e}")
    return None

# Los comandos bf y de se quedan igual, ya que llaman a esta función mejorada.
async def bf(ctx, usuario: discord.Member = None):
    if usuario is None: return await ctx.send("Debes mencionar a un usuario.")
    async with ctx.typing():
        gif = await get_giphy_gif("itadori black flash")
        embed = discord.Embed(title="⚡¡Black Flash!⚡", description=f"{ctx.author.mention} le ha hecho un **Black Flash** a {usuario.mention}.", color=discord.Color.red())
        if gif: embed.set_image(url=gif)
        else: embed.set_footer(text="No se encontró el GIF en Klipy")
        await ctx.send(embed=embed)

async def de(ctx, usuario: discord.Member = None):
    if usuario is None: return await ctx.send("Debes mencionar a un usuario.")
    async with ctx.typing():
        gif = await get_giphy_gif("jujutsu kaisen domain expansion")
        embed = discord.Embed(title="¡EXPANSION DE DOMINIO!", description=f"{ctx.author.mention} le ha expandido su **dominio** a {usuario.mention}", color=discord.Color.blue())
        if gif: embed.set_image(url=gif)
        else: embed.set_footer(text="No se encontró el GIF en Klipy")
        await ctx.send(embed=embed)