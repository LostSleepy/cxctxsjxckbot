import discord
from discord.ext import commands, tasks
import random
import json
import os
import time
import asyncio

AURA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aura_data.json")
CANAL_ANUNCIOS_ID = 1497645495051354113
ADMIN_ID = 979869404110159912

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

RAZONES_VICTORIA = [
    "Ganó porque el aura del rival estaba nivel chopped 💀.",
    "Ganó porque Ismael reencarnó y le echó una mano ✨.",
    "Ganó porque le copia los pasos a Jinwoo y entró en modo monarca 👤.",
    "Ganó porque el rival no tiene presencia en el server.",
    "Ganó porque desayunó bien y eso se nota en el aura.",
    "Ganó porque Sukuna le debe un favor de una vida pasada.",
    "Ganó porque el universo no podía permitir lo contrario.",
    "Ganó porque tenía el Wi-Fi más rápido y eso suma aura.",
    "Ganó porque Gojo le mandó apoyo espiritual desde el mas allá.",
    "Ganó por pura superioridad. No hay más explicación.",
]

MENSAJES_BF_RECORD = [
    "⚡⚡⚡ **RÉCORD DE DESTELLOS NEGROS** ⚡⚡⚡\n{mention} ha encadenado Destellos consecutivos. Aura **duplicada** a **{aura} pts**. Histórico.",
    "⚡ **DESTELLO NEGRO PERFECTO** ⚡\n{mention} ha rozado lo imposible. Su aura explota hasta **{aura} pts**.",
    "💥 **CONVERGENCIA DE ENERGÍA MALDITA** 💥\n{mention} lo ha hecho. Aura **x2** — ahora en **{aura} pts**. El server tiembla.",
]

aura_lock = asyncio.Lock()


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
    hoy = int(time.time() // 86400)
    entrada = data.get(user_id)
    if entrada is None or entrada.get("dia") != hoy:
        nuevo = random.randint(-1000, 5000)
        data[user_id] = {"valor": nuevo, "dia": hoy}
        guardar_aura(data)
    return data[user_id]["valor"]

def set_aura_usuario(data, user_id: str, valor: int):
    hoy = int(time.time() // 86400)
    data[user_id] = {"valor": valor, "dia": hoy}
    guardar_aura(data)

def get_aura_gif(puntos):
    if puntos >= 3000:
        return "https://static.klipy.com/ii/f87f46a2c5aeaeed4c68910815f73eaf/04/ff/lx7cJhef.gif"
    elif puntos >= 1000:
        return "https://static.klipy.com/ii/d7aec6f6f171607374b2065c836f92f4/c5/36/Fn6Mwx5L.gif"
    elif puntos >= 0:
        return "https://static.klipy.com/ii/35ccce3d852f7995dd2da910f2abd795/83/1d/miXnBam8.gif"
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
        self.votos_chopped = {}
        self.chopped_task.start()

    def cog_unload(self):
        self.chopped_task.cancel()

    async def _bypass_cooldown(self, ctx):
        if ctx.author.id == ADMIN_ID:
            ctx.command.reset_cooldown(ctx)

    # --- TASK CHOPPED ---
    @tasks.loop(hours=6)
    async def chopped_task(self):
        canal = self.bot.get_channel(CANAL_ANUNCIOS_ID)
        if canal is None:
            return
        humanos = [m for m in canal.guild.members if not m.bot]
        if not humanos:
            return
        elegido = random.choice(humanos)
        await canal.send(random.choice(MENSAJES_CHOPPED).format(mention=elegido.mention))

    @chopped_task.before_loop
    async def before_chopped(self):
        await self.bot.wait_until_ready()

    # --- AURA ---
    @commands.command(name="aura")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def aura(self, ctx, miembro: discord.Member = None):
        """Consulta tu aura del día (se resetea cada 24h)."""
        await self._bypass_cooldown(ctx)
        miembro = miembro or ctx.author
        async with aura_lock:
            puntos = get_aura_usuario(self.aura_data, str(miembro.id))
        embed = discord.Embed(
            title=f"✨ Aura de {miembro.display_name}",
            description=get_aura_msg(puntos),
            color=discord.Color.gold() if puntos >= 0 else discord.Color.dark_red()
        )
        embed.set_image(url=get_aura_gif(puntos))
        embed.set_footer(text="Se resetea cada 24h.")
        await ctx.send(embed=embed)

    # --- PICHA ---
    @commands.command(name="picha", aliases=["pp"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def picha(self, ctx, miembro: discord.Member = None):
        """Mide el tamaño con rigor científico."""
        await self._bypass_cooldown(ctx)
        miembro = miembro or ctx.author
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

    # --- VOTO CHOPPED ---
    @commands.command(name="vc", aliases=["votochopped"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def voto_chopped(self, ctx, usuario: discord.Member = None):
        """Vota para choppear a alguien. 3 votos en 5 min = timeout."""
        await self._bypass_cooldown(ctx)
        if usuario is None:
            return await ctx.send("❌ Menciona a alguien para votar.")
        if usuario.bot:
            return await ctx.send("❌ No puedes votar contra el bot.")
        if usuario.id == ctx.author.id:
            return await ctx.send("❌ No puedes votarte a ti mismo.")

        ahora = time.time()
        vid = str(usuario.id)
        if vid not in self.votos_chopped:
            self.votos_chopped[vid] = []
        self.votos_chopped[vid] = [
            (uid, ts) for uid, ts in self.votos_chopped[vid] if ahora - ts < 300
        ]
        if ctx.author.id in [uid for uid, _ in self.votos_chopped[vid]]:
            return await ctx.send("❌ Ya has votado contra esta persona recientemente.")

        self.votos_chopped[vid].append((ctx.author.id, ahora))
        total = len(self.votos_chopped[vid])

        if total >= 3:
            self.votos_chopped[vid] = []
            if ctx.guild.me.guild_permissions.moderate_members:
                from datetime import timedelta
                try:
                    await usuario.timeout(timedelta(minutes=5), reason="Voto Chopped.")
                    await ctx.send(f"💀 **CHOPPED.** {usuario.mention} silenciado 5 minutos.")
                except discord.Forbidden:
                    await ctx.send("❌ No tengo permisos para silenciar a esa persona.")
            else:
                await ctx.send("❌ Me falta el permiso `Moderate Members`.")
        else:
            await ctx.send(f"🗳️ Voto contra {usuario.mention}. **{total}/3** — faltan {3 - total}.")

    # --- DUELO DE AURA ---
    @commands.command(name="da", aliases=["dueloaura"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def duelo_aura(self, ctx, rival: discord.Member = None):
        """Duelo de aura. Ganador +50, perdedor -100."""
        await self._bypass_cooldown(ctx)
        if rival is None:
            return await ctx.send("❌ Menciona a tu rival.")
        if rival.bot:
            return await ctx.send("❌ El bot tiene inmunidad diplomática.")
        if rival.id == ctx.author.id:
            return await ctx.send("❌ No puedes duelarte contigo mismo.")

        async with aura_lock:
            aura_autor = get_aura_usuario(self.aura_data, str(ctx.author.id))
            aura_rival = get_aura_usuario(self.aura_data, str(rival.id))
            if aura_autor >= aura_rival:
                ganador, perdedor = ctx.author, rival
                aura_g, aura_p = aura_autor, aura_rival
            else:
                ganador, perdedor = rival, ctx.author
                aura_g, aura_p = aura_rival, aura_autor
            nueva_g = aura_g + 50
            nueva_p = aura_p - 100
            set_aura_usuario(self.aura_data, str(ganador.id), nueva_g)
            set_aura_usuario(self.aura_data, str(perdedor.id), nueva_p)

        razon = random.choice(RAZONES_VICTORIA)
        embed = discord.Embed(title="⚔️ Duelo de Aura", color=discord.Color.gold())
        embed.add_field(name="🏆 Ganador", value=f"{ganador.mention} — **{nueva_g} pts** (+50)", inline=False)
        embed.add_field(name="💀 Perdedor", value=f"{perdedor.mention} — **{nueva_p} pts** (-100)", inline=False)
        embed.add_field(name="📖 Lore", value=f"{ganador.mention} {razon}", inline=False)
        await ctx.send(embed=embed)

    # --- BF (fusionado desde jujutsu) ---
    @commands.command(name="bf", aliases=["blackflash"])
    async def bf_command(self, ctx, usuario: discord.Member = None):
        """Lanza un Black Flash. 5% de duplicar tu aura."""
        from comandos_gifs import bf as _bf
        await _bf(ctx, usuario)

        if usuario is None or usuario.bot or usuario.id == ctx.author.id:
            return

        if random.random() < 0.05:
            async with aura_lock:
                uid = str(ctx.author.id)
                hoy = int(time.time() // 86400)
                entrada = self.aura_data.get(uid)
                if entrada and entrada.get("dia") == hoy:
                    nueva = entrada["valor"] * 2
                else:
                    nueva = 100
                set_aura_usuario(self.aura_data, uid, nueva)

            canal = self.bot.get_channel(CANAL_ANUNCIOS_ID)
            if canal:
                msg = random.choice(MENSAJES_BF_RECORD).format(
                    mention=ctx.author.mention, aura=nueva
                )
                await canal.send(msg)

    # --- DE (fusionado desde jujutsu) ---
    @commands.command(name="de", aliases=["dominio"])
    async def de_command(self, ctx, usuario: discord.Member = None):
        """Ejecuta una Expansión de Dominio."""
        from comandos_gifs import de as _de
        await _de(ctx, usuario)

    # --- SETAURA (solo admin) ---
    @commands.command(name="setaura")
    async def set_aura_cmd(self, ctx, miembro: discord.Member = None, valor: int = None):
        """[Admin] Establece el aura de un usuario manualmente."""
        if ctx.author.id != ADMIN_ID:
            return
        if miembro is None or valor is None:
            return await ctx.send("Uso: `cx!setaura @usuario [valor]`")
        async with aura_lock:
            set_aura_usuario(self.aura_data, str(miembro.id), valor)
        await ctx.send(f"✅ Aura de {miembro.mention} establecida a **{valor} pts**.")

    # --- RESETAURA (solo admin) ---
    @commands.command(name="resetaura")
    async def reset_aura_cmd(self, ctx, miembro: discord.Member = None):
        """[Admin] Resetea el aura de un usuario."""
        if ctx.author.id != ADMIN_ID:
            return
        if miembro is None:
            return await ctx.send("Uso: `cx!resetaura @usuario`")
        async with aura_lock:
            self.aura_data.pop(str(miembro.id), None)
            guardar_aura(self.aura_data)
        await ctx.send(f"✅ Aura de {miembro.mention} reseteada.")


async def setup(bot):
    await bot.add_cog(Extras(bot))
