import discord
import os
import aiohttp
import random
from dotenv import load_dotenv

load_dotenv()

KLIPY_API_KEY = os.getenv('KLIPY_KEY')

async def get_giphy_gif(query):
    """Obtiene un GIF de Klipy con cabeceras de navegador para evitar el error 204."""
    if not KLIPY_API_KEY:
        print("❌ DEBUG: KLIPY_KEY no encontrada.")
        return None

    url = "https://api.klipy.com/v1/gifs/search"
    
    # Añadimos User-Agent para que Klipy no nos bloquee por parecer un bot
    headers = {
        "X-API-KEY": KLIPY_API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    params = {
        'q': query,
        'limit': 15  # Pedimos un poco más para tener variedad
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('data', [])
                    
                    if results:
                        gif_obj = random.choice(results)
                        # Klipy puede devolver la URL en diferentes campos según el tipo de archivo
                        images = gif_obj.get('images', {})
                        return images.get('original', {}).get('url') or images.get('fixed_height', {}).get('url')
                    
                    print(f"⚠️ DEBUG: Klipy devolvió 200 pero la lista 'data' está vacía para: {query}")
                
                elif response.status == 204:
                    print(f"❌ DEBUG: Error 204 - Klipy dice que no hay contenido para '{query}'. Probando término genérico...")
                    # Si falla el específico, intentamos uno que SIEMPRE tiene resultados en tu captura
                    return await get_giphy_gif("jujutsu kaisen") if query != "jujutsu kaisen" else None
                
                else:
                    print(f"❌ DEBUG: Status {response.status}. Msg: {await response.text()}")
                    
        except Exception as e:
            print(f"❌ DEBUG: Error de conexión: {e}")
    return None

async def bf(ctx, usuario: discord.Member = None):
    if usuario is None: return await ctx.send("Debes mencionar a un usuario.")
    async with ctx.typing():
        gif = await get_giphy_gif("itadori black flash")
        embed = discord.Embed(title="⚡¡Black Flash!⚡", description=f"{ctx.author.mention} le ha hecho un **Black Flash** a {usuario.mention}.", color=discord.Color.red())
        if gif: embed.set_image(url=gif)
        else: embed.set_footer(text="Klipy no entregó el GIF (Error 204/Empty)")
        await ctx.send(embed=embed)

async def de(ctx, usuario: discord.Member = None):
    if usuario is None: return await ctx.send("Debes mencionar a un usuario.")
    async with ctx.typing():
        gif = await get_giphy_gif("jujutsu kaisen domain expansion")
        embed = discord.Embed(title="¡EXPANSION DE DOMINIO!", description=f"{ctx.author.mention} le ha expandido su **dominio** a {usuario.mention}", color=discord.Color.blue())
        if gif: embed.set_image(url=gif)
        else: embed.set_footer(text="Klipy no entregó el GIF (Error 204/Empty)")
        await ctx.send(embed=embed)