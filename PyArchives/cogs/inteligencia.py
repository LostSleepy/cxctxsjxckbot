import discord
from discord.ext import commands
from google import genai
import os
import asyncio

# Configuración del cliente forzando la compatibilidad
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))

INSTRUCCIONES_SISTEMA = (
    "Eres Kasane teto, un bot de Discord inteligente y un poco sarcástico. "
    "Tu objetivo es ayudar a los usuarios del servidor. "
    "Si te preguntan por código, sé preciso. Si te hablan normal, sé divertido. "
    "Responde siempre de forma concisa."
)

class Inteligencia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.bot.user.mentioned_in(message):
            # Limpieza de mención
            contenido = message.content.replace(f'<@{self.bot.user.id}>', '').replace(f'<@!{self.bot.user.id}>', '').strip()

            if not contenido:
                return await message.reply("¿Me invocas para el silencio? Habla, humano.")

            async with message.channel.typing():
                try:
                    # Usamos el método más directo disponible en la nueva SDK
                    # Cambiamos 'gemini-1.5-flash' por 'models/gemini-1.5-flash' si el error persiste, 
                    # pero la SDK nueva prefiere el nombre corto.
                    response = await asyncio.to_thread(
                        client.models.generate_content,
                        model='gemini-1.5-flash',
                        contents=contenido,
                        config={'system_instruction': INSTRUCCIONES_SISTEMA}
                    )
                    
                    if response and response.text:
                        await message.reply(response.text[:1900])
                    else:
                        await message.reply("Mi energía maldita se ha dispersado. Intenta de nuevo.")

                except Exception as e:
                    print(f"❌ ERROR CRÍTICO GEMINI: {e}")
                    error_str = str(e)
                    if "429" in error_str:
                        await message.reply("⚠️ Límite de mensajes alcanzado. Descansa un poco.")
                    elif "404" in error_str:
                        # Intento de recuperación automática si falla el modelo flash
                        await message.reply("💢 El modelo no responde. Revisando conexión espiritual...")
                    else:
                        await message.reply(f"Error inesperado: {error_str[:50]}")

async def setup(bot):
    await bot.add_cog(Inteligencia(bot))