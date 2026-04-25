import discord
from discord.ext import commands
from discord.ext import tasks
import random
import json
import os
import time

# Archivo donde se guarda el aura de cada usuario
AURA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aura_data.json")
CANAL_ANUNCIOS_ID = 1497645495051354113

# --- MENSAJES DE CHOPPED ---
MENSAJES_CHOPPED = [
    "estás super chopped {mention} 💀",
    "{mention} eres un chopped de manual, lo siento.",
    "alguien tenía que decírtelo... {mention}, estás chopped.",
    "{mention} chopped detected. 🚨",
    "el bot ha decidido: {mention} está chopped hoy.",
    "{mention} ni el aura te salva, estás chopped. 📉",
    "aviso a la comunidad: {mention} está chopped. Proceded con cautela.",
    "{mention} ¿tú bien? porque el bot dice que no. Chopped total.",
    "análisis completado. Resultado: {mention} — chopped. 🔬",
    "{mention} te ha tocado. Estás chopped, asúmelo.",
]

# --- UTILS AURA ---
def cargar_aura():
    if os.path.exists(AURA_FILE):
        with open(AURA_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_aura(data):
    with open(AURA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_aura_usuario(data, user_id: str):
    hoy = int(time.time() // 86400)  # Día actual en epoch
    entrada = data.get(user_id)
    if entrada is None or entrada.get("dia") != hoy:
        # Reset diario: nuevo valor aleatorio
        nuevo = random.randint(-1000, 5000)
        data[user_id] = {"valor": nuevo, "dia": hoy}
        guardar_aura(data)
    return data[user_id]["valor"]

def get_aura_gif(puntos):
    if puntos >= 3000:
        return "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/6a/36/0uOGWmUeaFn1jb.gif"
    elif puntos >= 1000:
        return "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/17/17/xlNyC85ZaLUL7j.gif"
    elif puntos >= 0:
        return "https://static.klipy.com/ii/e293a233a303a98e471f78d04e13a1b0/74/b0/45Wwwv17.gif"
    else:
        return "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/a1/55/eMe2oFZQ3VtMfvGKEy.gif"

def get_aura_msg(puntos):
    if puntos >= 3000:
        return f"📈 **BRUTAL.** Tienes **{puntos}** puntos de aura. Eres el amo del server."
    elif puntos >= 1000:
        return f"✨ Tienes **{puntos}** puntos de aura. Respetable."
    elif puntos >= 0:
        return f"😐 Tienes **{puntos}** puntos de aura. Normalillo."
    else:
        return f"📉 **{puntos}** puntos de aura. Tocan fondo. Chopped energy."


class Extras(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.aura_data = cargar_aura()
        self.chopped_task.start()

    def cog_unload(self):
        self.chopped_task.cancel()

    # --- TASK: CHOPPED PERIÓDICO ---
    @tasks.loop(hours=6)
    async def chopped_task(self):
        canal = self.bot.get_channel(CANAL_ANUNCIOS_ID)
        if canal is None:
            return

        # Filtramos bots y cogemos un miembro aleatorio del servidor
        guild = canal.guild
        humanos = [m for m in guild.members if not m.bot]
        if not humanos:
            return

        elegido = random.choice(humanos)
        mensaje = random.choice(MENSAJES_CHOPPED).format(mention=elegido.mention)
        await canal.send(mensaje)

    @chopped_task.before_loop
    async def before_chopped(self):
        await self.bot.wait_until_ready()

    # --- COMANDO: AURA ---
    @commands.command(name="aura")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def aura(self, ctx, miembro: discord.Member = None):
        """Consulta tu aura del día (se resetea cada 24h)."""
        miembro = miembro or ctx.author
        puntos = get_aura_usuario(self.aura_data, str(miembro.id))
        gif = get_aura_gif(puntos)
        msg = get_aura_msg(puntos)

        embed = discord.Embed(
            title=f"✨ Aura de {miembro.display_name}",
            description=msg,
            color=discord.Color.gold() if puntos >= 0 else discord.Color.dark_red()
        )
        embed.set_image(url=gif)
        embed.set_footer(text="Se resetea cada 24h.")
        await ctx.send(embed=embed)

    # --- COMANDO: PICHA ---
    @commands.command(name="picha", aliases=["pp"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def picha(self, ctx, miembro: discord.Member = None):
        """Mide el tamaño con rigor científico."""
        miembro = miembro or ctx.author
        # Seed basada en el ID para que sea consistente por usuario
        r = random.Random(miembro.id + int(time.time() // 86400))
        cm = r.randint(0, 30)
        barra = "8" + "=" * cm + "D"

        if cm >= 20:
            comentario = "Dios mío. 😳"
        elif cm >= 12:
            comentario = "Respetable."
        elif cm >= 6:
            comentario = "Normal tirando a normal."
        else:
            comentario = "Hay que rezar."

        embed = discord.Embed(
            title=f"🔬 Análisis científico de {miembro.display_name}",
            description=f"**{cm} cm**\n`{barra}`\n\n{comentario}",
            color=discord.Color.purple()
        )
        embed.set_footer(text="Resultados actualizados cada 24h.")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Extras(bot))
