import discord
from discord.ext import commands

class Monitorear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # --- CONFIGURACIÓN DE OBJETIVOS ---
        self.id_1 = 1405353594844086343
        self.id_2 = 931222134670364682
        self.canal_citas_id = 1478182165966753843

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Monitorea si las dos IDs coexisten en voz para moverlas juntas."""
        
        # Solo actuamos si alguien ENTRA o se MUEVE de canal (no si se desconecta)
        if after.channel is None:
            return

        # Si el que se movió es uno de los dos objetivos...
        if member.id == self.id_1 or member.id == self.id_2:
            
            # Buscamos a ambos miembros en el servidor
            guild = member.guild
            m1 = guild.get_member(self.id_1)
            m2 = guild.get_member(self.id_2)
            canal_citas = self.bot.get_channel(self.canal_citas_id)

            # Verificamos: ¿Están ambos conectados a algún canal de voz?
            if m1 and m1.voice and m2 and m2.voice:
                
                # Verificamos: ¿Alguno de los dos NO está todavía en el canal de citas?
                if m1.voice.channel.id != self.canal_citas_id or m2.voice.channel.id != self.canal_citas_id:
                    try:
                        # ¡Movimiento sincronizado!
                        await m1.move_to(canal_citas, reason="Coexistencia detectada.")
                        await m2.move_to(canal_citas, reason="Coexistencia detectada.")
                        print(f"❤️ Coexistencia detectada: {m1.name} y {m2.name} movidos a citas.")
                    except Exception as e:
                        print(f"❌ Error en el imán de citas: {e}")

async def setup(bot):
    await bot.add_cog(Monitorear(bot))