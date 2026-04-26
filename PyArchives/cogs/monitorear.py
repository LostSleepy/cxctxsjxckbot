import discord
from discord.ext import commands
import random


class Monitorear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.id_1 = 1405353594844086343
        self.id_2 = 931222134670364682
        self.canal_citas_id = 1478182165966753843
        self.activo = True
        # {(user1_id, user2_id): True} — pares con orden de alejamiento activa
        self.ordenes_alejamiento = set()

    @commands.command(name="nxc")
    @commands.has_permissions(administrator=True)
    async def toggle_monitor(self, ctx):
        """Activa o desactiva el sistema de monitoreo de voz."""
        self.activo = not self.activo
        estado = "ACTIVADO" if self.activo else "DESACTIVADO"
        color = discord.Color.green() if self.activo else discord.Color.red()
        embed = discord.Embed(
            title="Sistema de Monitoreo",
            description=f"El imán de coexistencia ha sido **{estado}**.",
            color=color,
        )
        await ctx.send(embed=embed)

    @commands.command(name="oa", aliases=["ordenalejamiento"])
    @commands.has_permissions(administrator=True)
    async def orden_alejamiento(self, ctx, user1: discord.Member = None, user2: discord.Member = None):
        """Activa orden de alejamiento entre dos usuarios. Si coinciden en voz, se separan."""
        if user1 is None or user2 is None:
            return await ctx.send("❌ Menciona a los dos usuarios. Ej: `cx!oa @user1 @user2`")
        if user1.id == user2.id:
            return await ctx.send("❌ No puedes poner una orden entre la misma persona.")

        par = frozenset({user1.id, user2.id})

        if par in self.ordenes_alejamiento:
            self.ordenes_alejamiento.discard(par)
            await ctx.send(f"✅ Orden de alejamiento entre {user1.mention} y {user2.mention} **desactivada**.")
        else:
            self.ordenes_alejamiento.add(par)
            await ctx.send(
                f"🚫 Orden de alejamiento activada entre {user1.mention} y {user2.mention}. "
                f"Si coinciden en voz, {user2.mention} será movido automáticamente."
            )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # --- IMÁN DE CITAS ---
        if self.activo and after.channel is not None:
            if member.id == self.id_1 or member.id == self.id_2:
                guild = member.guild
                m1 = guild.get_member(self.id_1)
                m2 = guild.get_member(self.id_2)
                canal_citas = self.bot.get_channel(self.canal_citas_id)

                if m1 and m1.voice and m2 and m2.voice:
                    if (
                        m1.voice.channel.id != self.canal_citas_id
                        or m2.voice.channel.id != self.canal_citas_id
                    ):
                        try:
                            await m1.move_to(canal_citas, reason="Coexistencia detectada.")
                            await m2.move_to(canal_citas, reason="Coexistencia detectada.")
                        except Exception as e:
                            print(f"❌ Error en imán de citas: {e}")

        # --- ORDEN DE ALEJAMIENTO ---
        if after.channel is not None and self.ordenes_alejamiento:
            par = None
            otro = None
            for p in self.ordenes_alejamiento:
                if member.id in p:
                    otro_id = next(uid for uid in p if uid != member.id)
                    otro = member.guild.get_member(otro_id)
                    par = p
                    break

            if otro and otro.voice and otro.voice.channel == after.channel:
                # Están en el mismo canal — movemos al segundo al azar
                canales_disponibles = [
                    c for c in member.guild.voice_channels
                    if c.id != after.channel.id and c.permissions_for(member.guild.me).move_members
                ]
                if canales_disponibles:
                    destino = random.choice(canales_disponibles)
                    try:
                        await otro.move_to(destino, reason="Orden de alejamiento activa.")
                        print(f"🚫 Orden de alejamiento: {otro.name} movido a {destino.name}.")
                    except Exception as e:
                        print(f"❌ Error en orden de alejamiento: {e}")


async def setup(bot):
    await bot.add_cog(Monitorear(bot))
