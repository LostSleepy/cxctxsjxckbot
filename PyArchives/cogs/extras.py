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
    "Ganó porque Gojo le mandó apoyo espiritual desde el más allá.",
    "Ganó por pura superioridad. No hay más explicación.",
]

MENSAJES_BF_RECORD = [
    "⚡⚡⚡ **RÉCORD DE DESTELLOS NEGROS** ⚡⚡⚡\n{mention} ha encadenado Destellos consecutivos. Aura **duplicada** a **{aura} pts**. Histórico.",
    "⚡ **DESTELLO NEGRO PERFECTO** ⚡\n{mention} ha rozado lo imposible. Su aura explota hasta **{aura} pts**.",
    "💥 **CONVERGENCIA DE ENERGÍA MALDITA** 💥\n{mention} lo ha hecho. Aura **x2** — ahora en **{aura} pts**. El server tiembla.",
]

CASTIGOS = [
    {"tipo": "mute",     "duracion": 60,  "emoji": "🔇", "msg": "silenciado 1 minuto."},
    {"tipo": "mute",     "duracion": 300, "emoji": "🔇", "msg": "silenciado 5 minutos. A pensar."},
    {"tipo": "deaf",     "duracion": 60,  "emoji": "🙉", "msg": "sordo durante 1 minuto. Modo monje."},
    {"tipo": "deaf",     "duracion": 300, "emoji": "🙉", "msg": "sordo durante 5 minutos."},
    {"tipo": "kick",     "duracion": 0,   "emoji": "📵", "msg": "expulsado de la llamada. Adiós."},
    {"tipo": "timeout",  "duracion": 60,  "emoji": "⏳", "msg": "en timeout 1 minuto."},
    {"tipo": "timeout",  "duracion": 300, "emoji": "⏳", "msg": "en timeout 5 minutos."},
    {"tipo": "mute_deaf","duracion": 120, "emoji": "💀", "msg": "sin micro y sin oír 2 minutos. Aislamiento total."},
]

VERSUS_VICTORIA = [
    "porque {perdedor} se quedó sin batería en el momento crítico.",
    "porque {perdedor} no sabe ni ponerse los zapatos.",
    "porque {perdedor} llegó tarde y ya había terminado todo.",
    "porque el aura de {perdedor} estaba en negativo ese día.",
    "porque {perdedor} se distrajo mirando el móvil.",
    "porque Sukuna eligió bando y no fue el de {perdedor}.",
    "porque {perdedor} intentó spamear y le falló el ping.",
    "porque el universo tiene favoritos y {perdedor} no es uno.",
    "porque {perdedor} confió demasiado en sus posibilidades.",
    "porque simplemente no había color. Lo siento, {perdedor}.",
]

aura_lock = asyncio.Lock()
recordatorios_activos = []


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

    # --- TOP AURA ---
    @commands.command(name="top", aliases=["ranking", "leaderboard"])
    async def top_aura(self, ctx):
        """Ranking de aura del server."""
        await self._bypass_cooldown(ctx)
        async with aura_lock:
            data = cargar_aura()

        hoy = int(time.time() // 86400)
        ranking = []
        for uid, entrada in data.items():
            if entrada.get("dia") != hoy:
                continue
            miembro = ctx.guild.get_member(int(uid))
            if miembro and not miembro.bot:
                ranking.append((miembro.display_name, entrada["valor"]))

        if not ranking:
            return await ctx.send("📊 Nadie ha consultado su aura hoy todavía.")

        ranking.sort(key=lambda x: x[1], reverse=True)
        top = ranking[:10]

        medallas = ["🥇", "🥈", "🥉"] + ["🔹"] * 7
        lineas = []
        for i, (nombre, puntos) in enumerate(top):
            lineas.append(f"{medallas[i]} **{nombre}** — {puntos} pts")

        embed = discord.Embed(
            title="📊 Ranking de Aura — Top 10",
            description="\n".join(lineas),
            color=discord.Color.gold()
        )
        embed.set_footer(text="Solo usuarios que han consultado su aura hoy.")
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
        """Duelo de aura aleatorio. Ganador +50, perdedor -100."""
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

            if random.random() < 0.5:
                ganador, perdedor = ctx.author, rival
                aura_g, aura_p = aura_autor, aura_rival
            else:
                ganador, perdedor = rival, ctx.author
                aura_g, aura_p = aura_rival, aura_autor

            nueva_g = aura_g + 50
            nueva_p = aura_p - 100
            set_aura_usuario(self.aura_data, str(ganador.id), nueva_g)
            set_aura_usuario(self.aura_data, str(perdedor.id), nueva_p)

        razon = random.choice(VERSUS_VICTORIA).format(perdedor=perdedor.display_name)
        embed = discord.Embed(title="⚔️ Duelo de Aura", color=discord.Color.gold())
        embed.add_field(name="🏆 Ganador", value=f"{ganador.mention} — **{nueva_g} pts** (+50)", inline=False)
        embed.add_field(name="💀 Perdedor", value=f"{perdedor.mention} — **{nueva_p} pts** (-100)", inline=False)
        embed.add_field(name="📖 Lore", value=f"{ganador.mention} ganó {razon}", inline=False)
        await ctx.send(embed=embed)

    # --- ROBO DE AURA ---
    @commands.command(name="robar", aliases=["rob"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def robar_aura(self, ctx, objetivo: discord.Member = None):
        """Intenta robar aura. 50% de éxito, si fallas pierdes tú."""
        await self._bypass_cooldown(ctx)
        if objetivo is None:
            return await ctx.send("❌ Menciona a quién quieres robar.")
        if objetivo.bot:
            return await ctx.send("❌ El bot no tiene aura robable.")
        if objetivo.id == ctx.author.id:
            return await ctx.send("❌ No puedes robarte a ti mismo.")

        cantidad = random.randint(50, 300)

        async with aura_lock:
            aura_ladr = get_aura_usuario(self.aura_data, str(ctx.author.id))
            aura_obj = get_aura_usuario(self.aura_data, str(objetivo.id))

            if random.random() < 0.5:
                # Éxito
                set_aura_usuario(self.aura_data, str(ctx.author.id), aura_ladr + cantidad)
                set_aura_usuario(self.aura_data, str(objetivo.id), aura_obj - cantidad)
                await ctx.send(
                    f"🥷 **ROBO EXITOSO.** {ctx.author.mention} le ha birlado **{cantidad} pts** de aura a {objetivo.mention}. Sin dejar rastro."
                )
            else:
                # Fallo — pierdes tú
                set_aura_usuario(self.aura_data, str(ctx.author.id), aura_ladr - cantidad)
                await ctx.send(
                    f"💀 **PILLADO.** {ctx.author.mention} intentó robarle a {objetivo.mention} y le salió mal. Pierde **{cantidad} pts** de aura."
                )

    # --- CASTIGO ---
    @commands.command(name="castigo", aliases=["cast"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def castigo(self, ctx, usuario: discord.Member = None):
        """Sentencia a alguien con un castigo aleatorio."""
        await self._bypass_cooldown(ctx)
        if usuario is None:
            return await ctx.send("❌ Menciona a alguien para castigar.")
        if usuario.bot:
            return await ctx.send("❌ El bot no acepta castigos.")
        if usuario.id == ctx.author.id:
            return await ctx.send("❌ No puedes castigarte a ti mismo. O sí, pero qué triste.")

        castigo = random.choice(CASTIGOS)
        tipo = castigo["tipo"]
        dur = castigo["duracion"]
        emoji = castigo["emoji"]
        msg = castigo["msg"]

        # Ejecutamos la acción real
        try:
            if tipo == "mute":
                if not usuario.voice:
                    return await ctx.send("❌ Esa persona no está en un canal de voz.")
                await usuario.edit(mute=True)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
                if dur:
                    await asyncio.sleep(dur)
                    await usuario.edit(mute=False)
            elif tipo == "deaf":
                if not usuario.voice:
                    return await ctx.send("❌ Esa persona no está en un canal de voz.")
                await usuario.edit(deafen=True)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
                if dur:
                    await asyncio.sleep(dur)
                    await usuario.edit(deafen=False)
            elif tipo == "mute_deaf":
                if not usuario.voice:
                    return await ctx.send("❌ Esa persona no está en un canal de voz.")
                await usuario.edit(mute=True, deafen=True)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
                if dur:
                    await asyncio.sleep(dur)
                    await usuario.edit(mute=False, deafen=False)
            elif tipo == "kick":
                if not usuario.voice:
                    return await ctx.send("❌ Esa persona no está en un canal de voz.")
                await usuario.move_to(None)
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
            elif tipo == "timeout":
                from datetime import timedelta
                await usuario.timeout(timedelta(seconds=dur), reason=f"Castigo de {ctx.author.display_name}")
                await ctx.send(f"{emoji} {usuario.mention} queda {msg}")
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para ejecutar ese castigo.")

    # --- VERSUS ---
    @commands.command(name="vs", aliases=["versus"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def versus(self, ctx, u1: discord.Member = None, u2: discord.Member = None):
        """Decide quién ganaría en un combate entre dos usuarios."""
        await self._bypass_cooldown(ctx)
        if u1 is None or u2 is None:
            return await ctx.send("❌ Menciona a dos usuarios. Ej: `cx!vs @u1 @u2`")
        if u1.id == u2.id:
            return await ctx.send("❌ No puedes enfrentar a alguien consigo mismo.")

        ganador, perdedor = random.sample([u1, u2], 2)
        razon = random.choice(VERSUS_VICTORIA).format(perdedor=perdedor.display_name)

        embed = discord.Embed(
            title="🥊 VERSUS",
            description=f"**{u1.display_name}** VS **{u2.display_name}**",
            color=discord.Color.orange()
        )
        embed.add_field(name="🏆 Ganador", value=f"{ganador.mention}", inline=True)
        embed.add_field(name="💀 Perdedor", value=f"{perdedor.mention}", inline=True)
        embed.add_field(name="📖 Motivo", value=f"{ganador.mention} ganó {razon}", inline=False)
        await ctx.send(embed=embed)

    # --- DADO ---
    @commands.command(name="dado", aliases=["dice", "d"])
    async def dado(self, ctx, caras: int = 6):
        """Lanza un dado. cx!dado [caras] — por defecto d6."""
        await self._bypass_cooldown(ctx)
        if caras < 2 or caras > 1000:
            return await ctx.send("❌ El dado tiene que tener entre 2 y 1000 caras.")
        resultado = random.randint(1, caras)
        await ctx.send(f"🎲 **d{caras}** → `{resultado}`")

    # --- RECORDAR ---
    @commands.command(name="recordar", aliases=["reminder", "rem"])
    async def recordar(self, ctx, tiempo: str = None, *, mensaje: str = None):
        """Crea un recordatorio. Ej: cx!recordar 10m Llamar a alguien"""
        await self._bypass_cooldown(ctx)
        if tiempo is None or mensaje is None:
            return await ctx.send("❌ Uso: `cx!recordar [tiempo] [mensaje]`\nEjemplo: `cx!recordar 10m Sacar al perro`")

        # Parsear tiempo
        unidad = tiempo[-1].lower()
        try:
            valor = int(tiempo[:-1])
        except ValueError:
            return await ctx.send("❌ Formato de tiempo inválido. Usa `10m`, `2h` o `30s`.")

        if unidad == "s":
            segundos = valor
        elif unidad == "m":
            segundos = valor * 60
        elif unidad == "h":
            segundos = valor * 3600
        else:
            return await ctx.send("❌ Unidad no válida. Usa `s` (segundos), `m` (minutos) o `h` (horas).")

        if segundos > 86400:
            return await ctx.send("❌ Máximo 24 horas de recordatorio.")

        await ctx.send(f"⏰ Recordatorio establecido. Te aviso en **{tiempo}**.")

        async def _recordar():
            await asyncio.sleep(segundos)
            try:
                await ctx.author.send(f"⏰ **Recordatorio:** {mensaje}")
            except discord.Forbidden:
                await ctx.send(f"⏰ {ctx.author.mention} — tu recordatorio: **{mensaje}**")

        asyncio.create_task(_recordar())

    # --- BF ---
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

    # --- HOLA ---
    @commands.command(name="hola", aliases=["hello", "hi"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def hola(self, ctx):
        """Saludo con GIF aleatorio."""
        await self._bypass_cooldown(ctx)
        from comandos_gifs import get_giphy_gif
        gif = await get_giphy_gif("hola")
        embed = discord.Embed(
            title=f"👋 ¡Hola, {ctx.author.display_name}!",
            color=discord.Color.from_rgb(255, 105, 180)
        )
        embed.set_image(url=gif)
        await ctx.send(embed=embed)

    # --- DE ---
    @commands.command(name="de", aliases=["dominio"])
    async def de_command(self, ctx, usuario: discord.Member = None):
        """Ejecuta una Expansión de Dominio."""
        from comandos_gifs import de as _de
        await _de(ctx, usuario)

    # --- SETAURA (admin) ---
    @commands.command(name="setaura")
    async def set_aura_cmd(self, ctx, miembro: discord.Member = None, valor: int = None):
        if ctx.author.id != ADMIN_ID:
            return
        if miembro is None or valor is None:
            return await ctx.send("Uso: `cx!setaura @usuario [valor]`")
        async with aura_lock:
            set_aura_usuario(self.aura_data, str(miembro.id), valor)
        await ctx.send(f"✅ Aura de {miembro.mention} establecida a **{valor} pts**.")

    # --- RESETAURA (admin) ---
    @commands.command(name="resetaura")
    async def reset_aura_cmd(self, ctx, miembro: discord.Member = None):
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
