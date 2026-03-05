import discord
from discord.ext import commands


class Monitorear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # --- CONFIGURACIÓN DE OBJETIVOS ---
        self.id_1 = 1405353594844086343
        self.id_2 = 931222134670364682
        self.canal_citas_id = 1478182165966753843

        # --- ESTADO DEL SISTEMA ---
        self.activo = True  # Por defecto empieza activado

    @commands.command(name="nxc")
    @commands.has_permissions(administrator=True)  # Recomendado: solo para admins
    async def toggle_monitor(self, ctx):
        """Activa o desactiva el movimiento automático de objetivos."""
        self.activo = not self.activo
        estado = "ACTIVADO" if self.activo else "DESACTIVADO"
        color = discord.Color.green() if self.activo else discord.Color.red()

        embed = discord.Embed(
            title="Sistema de Monitoreo",
            description=f"El imán de coexistencia ha sido **{estado}**.",
            color=color,
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Monitorea si las dos IDs coexisten en voz para moverlas juntas."""

        # 1. Verificamos si el sistema está activo
        if not self.activo:
            return

        # 2. Solo actuamos si alguien ENTRA o se MUEVE de canal
        if after.channel is None:
            return

        # 3. Si el que se movió es uno de los dos objetivos...
        if member.id == self.id_1 or member.id == self.id_2:

            guild = member.guild
            m1 = guild.get_member(self.id_1)
            m2 = guild.get_member(self.id_2)
            canal_citas = self.bot.get_channel(self.canal_citas_id)

            # Verificamos: ¿Están ambos conectados a algún canal de voz?
            if m1 and m1.voice and m2 and m2.voice:

                # Verificamos: ¿Alguno de los dos NO está todavía en el canal de citas?
                if (
                    m1.voice.channel.id != self.canal_citas_id
                    or m2.voice.channel.id != self.canal_citas_id
                ):
                    try:
                        # Movimiento sincronizado
                        await m1.move_to(
                            canal_citas,
                            reason="Coexistencia detectada (Sistema Activo).",
                        )
                        await m2.move_to(
                            canal_citas,
                            reason="Coexistencia detectada (Sistema Activo).",
                        )
                        print(
                            f"❤️ Coexistencia detectada: {m1.name} y {m2.name} movidos a citas."
                        )
                    except Exception as e:
                        print(f"❌ Error en el imán de citas: {e}")


async def setup(bot):
    await bot.add_cog(Monitorear(bot))
