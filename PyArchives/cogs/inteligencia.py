import discord
from discord.ext import commands
from google import genai # Nueva librería oficial
import os
import asyncio

# Configuración con la nueva SDK
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))

INSTRUCCIONES_SISTEMA = (
    "Eres Kasane Teto, un bot de Discord inteligente y un poco sarcástico. "
    "Tu objetivo es ayudar a los usuarios del servidor. "
    "Si te preguntan por código, sé preciso. Si te hablan normal, sé divertido. "
    "Responde siempre de forma concisa. Y ten especial aprecio por Dvix, sobre todo si te hablan sobre el di que es fan aferrimo de los pies"
)

class Inteligencia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.bot.user.mentioned_in(message):
            contenido = message.content.replace(f'<@{self.bot.user.id}>', '').replace(f'<@!{self.bot.user.id}>', '').strip()

            if not contenido:
                return await message.reply("¿Qué quieres, humano?")

            async with message.channel.typing():
                try:
                    # La nueva forma de llamar al modelo en 2026
                    # Usamos 'gemini-1.5-flash' directamente sin prefijos raros
                    response = await asyncio.to_thread(
                        client.models.generate_content,
                        model='gemini-1.5-flash',
                        contents=contenido,
                        config={'system_instruction': INSTRUCCIONES_SISTEMA}
                    )
                    
                    if response.text:
                        await message.reply(response.text[:1900])
                    else:
                        await message.reply("Mi energía maldita se ha agotado temporalmente.")

                except Exception as e:
                    print(f"❌ ERROR GEMINI NUEVO: {e}")
                    # Control de cuota (Rate Limit)
                    if "429" in str(e):
                        await message.reply("⚠️ He hablado demasiado. Vuelve en unos minutos.")
                    else:
                        await message.reply("Error en la conexión con el plano espiritual (API Error).")

async def setup(bot):
    await bot.add_cog(Inteligencia(bot))