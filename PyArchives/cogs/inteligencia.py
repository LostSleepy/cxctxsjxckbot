import discord
from discord.ext import commands
import google.generativeai as genai
import os
import asyncio

# Configuración de Google Gemini
genai.configure(api_key=os.getenv("GEMINI_KEY"))

# Definimos las instrucciones del sistema para que sepa quién es
INSTRUCCIONES_SISTEMA = (
    "Eres 'Kasane Teto, un bot de Discord inteligente y un poco sarcástico. "
    "Tu objetivo es ayudar a los usuarios del servidor. "
    "Si te preguntan por código o programación, sé muy preciso y riguroso. "
    "Si te hablan normal, sé divertido pero mantén un tono gracioso. "
    "Responde siempre de forma concisa (máximo 2 párrafos) para no saturar el chat."
)

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=INSTRUCCIONES_SISTEMA
)

class Inteligencia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Reglas de seguridad básicas
        if message.author.bot:
            return

        # El bot responderá si lo mencionan (ej: @Bot hola)
        if self.bot.user.mentioned_in(message):
            # Limpiamos la mención del texto para que no ensucie el prompt
            contenido = message.content.replace(f'<@{self.bot.user.id}>', '').replace(f'<@!{self.bot.user.id}>', '').strip()

            if not contenido:
                return await message.reply("¿Me mencionas para nada? No me hagas perder el tiempo.")

            async with message.channel.typing():
                try:
                    # Usamos asyncio.to_thread para que la llamada a la API no bloquee el bot
                    response = await asyncio.to_thread(
                        model.generate_content, 
                        contenido
                    )
                    
                    if response.text:
                        # Si la respuesta es muy larga, Discord dará error. Cortamos por si acaso.
                        respuesta_final = response.text[:1900]
                        await message.reply(respuesta_final)
                    else:
                        await message.reply("Vaya, mi energía maldita se ha dispersado. Intenta preguntar otra cosa.")

                except Exception as e:
                    print(f"❌ ERROR GEMINI: {e}")
                    # Error 429 es el de límite de cuota (gratis)
                    if "429" in str(e):
                        await message.reply("⚠️ He hablado demasiado por hoy. Mis límites gratuitos se han agotado, vuelve mañana.")
                    else:
                        await message.reply("Hubo un error en mi núcleo de IA. Revisa los logs de Koyeb.")

async def setup(bot):
    await bot.add_cog(Inteligencia(bot))