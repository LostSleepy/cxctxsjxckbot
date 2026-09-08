"""Admin cog: owner-only operations (say, DM, announce, data, maintenance).

All commands here require the configured admin. They fail silently
for anyone else (via the shared check) so the admin ID is not leaked
through error messages.
"""

from __future__ import annotations

import logging
import os
import platform
import sys
import time
from pathlib import Path

import discord
from config import (
    AURA_DATA_PATH,
    BACKUP_DIR,
    BASE_DIR,
    BLACKLIST_PATH,
    CANAL_ANUNCIOS_ID,
    MAINTENANCE_PATH,
    MAX_SAY_CHARS,
    SHIP_DATA_PATH,
    VCBAN_PATH,
)
from core.checks import is_admin
from core.store import load_json_safe
from discord.ext import commands

log = logging.getLogger(__name__)


def _aura_stats() -> tuple[int, int]:
    """Return (users_with_aura_today, average). Handles the {'valor','dia'} shape."""
    from core.settings import AURA_DATA_PATH as _p

    data = load_json_safe(_p, {})
    if not isinstance(data, dict) or not data:
        return 0, 0
    today = int(time.time() // 86400)
    values = [
        e.get("valor", 0) for e in data.values() if isinstance(e, dict) and e.get("dia") == today
    ]
    if not values:
        return 0, 0
    return len(values), round(sum(values) / len(values))


class Admin(commands.Cog):
    """Owner-only bot administration."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._start_time: float = time.time()
        # State services are provided by the bot instance (wired in main).
        # Fall back to direct instances so the cog also works standalone.

    def _blacklist(self):
        return getattr(self.bot, "blacklist", None)

    def _maintenance(self):
        return getattr(self.bot, "maintenance", None)

    # -- speak ----------------------------------------------------------
    @commands.command(name="decir", aliases=["say"])
    @is_admin()
    async def decir(self, ctx: commands.Context, *, mensaje: str | None = None) -> None:
        """[Admin] Teto repite tu mensaje en el canal actual."""
        if not mensaje:
            await ctx.send("❌ Usa: `cx!decir <mensaje>`")
            return
        if len(mensaje) > MAX_SAY_CHARS:
            await ctx.send(f"❌ Máximo {MAX_SAY_CHARS} caracteres.")
            return
        try:
            await ctx.message.delete()
        except discord.DiscordException:
            pass
        await ctx.send(mensaje[:MAX_SAY_CHARS])

    @commands.command(name="dm", aliases=["md", "mensajedirecto"])
    @is_admin()
    async def dm_user(
        self,
        ctx: commands.Context,
        usuario: discord.Member | None = None,
        *,
        mensaje: str | None = None,
    ) -> None:
        """[Admin] Envía un mensaje privado a un usuario."""
        if not usuario or not mensaje:
            await ctx.send("❌ Usa: `cx!dm @usuario <mensaje>`")
            return
        if len(mensaje) > MAX_SAY_CHARS:
            await ctx.send(f"❌ Máximo {MAX_SAY_CHARS} caracteres.")
            return
        try:
            embed = discord.Embed(
                title="📩 Mensaje de Teto",
                description=mensaje[:MAX_SAY_CHARS],
                color=discord.Color.blurple(),
            )
            embed.set_footer(text="🥖 Teto te ha enviado un mensaje")
            await usuario.send(embed=embed)
            await ctx.send(f"✅ Mensaje enviado a **{usuario.display_name}**.", delete_after=5)
        except discord.Forbidden:
            await ctx.send(
                f"❌ No pude enviar MD a **{usuario.display_name}**. Tiene los MDs cerrados."
            )
        except discord.DiscordException:
            log.warning("DM fallido a %s", usuario.id, exc_info=True)
            await ctx.send("❌ No se pudo enviar el mensaje. Inténtalo más tarde.")

    @commands.command(name="anuncio", aliases=["announce", "avisar"])
    @is_admin()
    async def anuncio(self, ctx: commands.Context, *, texto: str | None = None) -> None:
        """[Admin] Publica un anuncio formateado en el canal de anuncios."""
        if not texto:
            await ctx.send("❌ Usa: `cx!anuncio <texto>`")
            return
        if ctx.guild is None:
            await ctx.send("❌ Este comando solo funciona en un servidor.")
            return
        if len(texto) > MAX_SAY_CHARS:
            await ctx.send(f"❌ Máximo {MAX_SAY_CHARS} caracteres.")
            return
        if not CANAL_ANUNCIOS_ID:
            await ctx.send("❌ No hay canal de anuncios configurado (CANAL_ANUNCIOS_ID).")
            return
        canal = ctx.guild.get_channel(CANAL_ANUNCIOS_ID)
        if canal is None:
            try:
                canal = await ctx.guild.fetch_channel(CANAL_ANUNCIOS_ID)
            except discord.DiscordException:
                canal = None
        if canal is None:
            await ctx.send("❌ No encuentro el canal de anuncios configurado.")
            return
        embed = discord.Embed(
            title="📢 ¡Atención!",
            description=texto,
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text="Anuncio oficial • Teto")
        try:
            await canal.send(embed=embed)
        except discord.DiscordException:
            await ctx.send("❌ No tengo permiso para escribir en el canal de anuncios.")
            return
        await ctx.send(f"✅ Anuncio enviado a {canal.mention}.", delete_after=5)

    # -- data -----------------------------------------------------------
    @commands.command(name="backup", aliases=["exportar", "respaldar"])
    @is_admin()
    async def backup_data(self, ctx: commands.Context) -> None:
        """[Admin] Exporta todos los datos del bot a JSON."""
        await ctx.send("⏳ Generando respaldo...")
        data = {
            "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
            "servidor": ctx.guild.name if ctx.guild else "Desconocido",
            "miembros": ctx.guild.member_count if ctx.guild else 0,
            "aura": load_json_safe(AURA_DATA_PATH, {}),
            "ship": load_json_safe(SHIP_DATA_PATH, {}),
            "blacklist": load_json_safe(BLACKLIST_PATH, {}),
            "maintenance": load_json_safe(MAINTENANCE_PATH, {}),
            "vcban": load_json_safe(VCBAN_PATH, {}),
        }
        BACKUP_DIR.mkdir(exist_ok=True)
        backup_path = BACKUP_DIR / f"teto_backup_{time.strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import json

            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError:
            await ctx.send("❌ No se pudo escribir el archivo de respaldo.")
            return
        embed = discord.Embed(
            title="💾 Backup completado",
            description="Todos los datos han sido exportados.",
            color=discord.Color.green(),
        )
        embed.add_field(name="📁 Archivo", value=f"`{backup_path.name}`", inline=True)
        try:
            size_kb = backup_path.stat().st_size / 1024
        except OSError:
            size_kb = 0
        embed.add_field(name="📦 Tamaño", value=f"{size_kb:.1f} KB", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="stats", aliases=["botinfo"])
    @is_admin()
    async def stats(self, ctx: commands.Context) -> None:
        """[Admin] Dashboard del estado del bot."""
        uptime_secs = int(time.time() - self._start_time)
        days, rem = divmod(uptime_secs, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        total_guilds = len(self.bot.guilds)
        total_users = sum(g.member_count or 0 for g in self.bot.guilds)
        loaded_cogs = len(self.bot.cogs)
        total_cmds = len([c for c in self.bot.commands if not c.hidden])
        latency_ms = round(self.bot.latency * 1000) if not self.bot.is_closed() else -1
        aura_users, aura_avg = _aura_stats()

        embed = discord.Embed(
            title="📊 Dashboard — Teto Bot", color=discord.Color.from_rgb(255, 105, 180)
        )
        if self.bot.user is not None:
            try:
                embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            except Exception:
                pass
        embed.add_field(name="🟢 Latencia", value=f"`{latency_ms}ms`", inline=True)
        embed.add_field(
            name="🕒 Uptime", value=f"`{days}d {hours}h {minutes}m {seconds}s`", inline=True
        )
        embed.add_field(name="🏠 Servidores", value=f"`{total_guilds}`", inline=True)
        embed.add_field(name="👥 Usuarios totales", value=f"`{total_users}`", inline=True)
        embed.add_field(name="⚙️ Cogs cargados", value=f"`{loaded_cogs}`", inline=True)
        embed.add_field(name="📋 Comandos", value=f"`{total_cmds}`", inline=True)
        embed.add_field(name="✨ Usuarios con aura", value=f"`{aura_users}`", inline=True)
        embed.add_field(name="📊 Aura media", value=f"`{aura_avg} pts`", inline=True)
        embed.add_field(name="🐍 Python", value=f"`{sys.version.split()[0]}`", inline=True)
        embed.add_field(name="🤖 discord.py", value=f"`{discord.__version__}`", inline=True)
        embed.add_field(
            name="💻 OS", value=f"`{platform.system()} {platform.release()[:20]}`", inline=True
        )
        embed.set_footer(
            text=f"Solicitado por {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )
        await ctx.send(embed=embed)

    @commands.command(name="reload", aliases=["recargar"])
    @is_admin()
    async def reload_cog(self, ctx: commands.Context, cog_name: str | None = None) -> None:
        """[Admin] Recarga un cog o todos sin reiniciar."""
        if cog_name:
            extension = f"cogs.{cog_name.lower()}"
            try:
                await self.bot.reload_extension(extension)
                await ctx.send(f"✅ Cog **{cog_name}** recargado.")
            except Exception as e:
                log.warning("Reload %s falló: %s", extension, e)
                await ctx.send(f"❌ Error recargando **{cog_name}**.")
        else:
            cogs_dir = Path(__file__).resolve().parent
            reloaded, errors = 0, 0
            for filename in sorted(os.listdir(cogs_dir)):
                if filename.endswith(".py") and not filename.startswith("__"):
                    try:
                        await self.bot.reload_extension(f"cogs.{filename[:-3]}")
                        reloaded += 1
                    except Exception as e:
                        errors += 1
                        log.warning("Reload cogs.%s falló: %s", filename[:-3], e)
            color = discord.Color.green() if not errors else discord.Color.orange()
            await ctx.send(
                embed=discord.Embed(
                    title="🔄 Reload completo",
                    description=f"✅ **{reloaded}** recargados. ❌ **{errors}** errores.",
                    color=color,
                )
            )

    @commands.command(name="logs", aliases=["log"])
    @is_admin()
    async def logs_cmd(self, ctx: commands.Context, lineas: int = 15) -> None:
        """[Admin] Últimas líneas del log. Uso: `cx!logs [N]` (máx 40)."""
        lineas = max(1, min(lineas, 40))
        log_path = BASE_DIR / "logs" / "bot.log"
        if not log_path.exists():
            await ctx.send("❌ No se encontró el archivo de logs.")
            return
        try:
            with open(log_path, encoding="utf-8") as f:
                all_lines = f.readlines()
        except OSError:
            await ctx.send("❌ No se pudo leer el archivo de logs.")
            return
        last = all_lines[-lineas:]
        content = "".join(last)
        if len(content) > 1900:
            content = "..." + content[-1900:]
        embed = discord.Embed(
            title=f"📋 Últimas {len(last)} líneas de log",
            description=f"```\n{content}```",
            color=discord.Color.dark_grey(),
        )
        embed.set_footer(text=f"{log_path.name} • {len(all_lines)} líneas totales")
        await ctx.send(embed=embed)

    # -- blacklist ------------------------------------------------------
    @commands.command(name="blacklist", aliases=["bl"])
    @is_admin()
    async def blacklist_user(
        self, ctx: commands.Context, usuario: discord.Member | None = None
    ) -> None:
        """[Admin] Bloquea a un usuario de todos los comandos."""
        svc = self._blacklist()
        if usuario is None:
            await ctx.send("❌ Usa: `cx!blacklist @usuario`")
            return
        if svc is None:  # pragma: no cover - wiring fallback
            await ctx.send("❌ Servicio de blacklist no disponible.")
            return
        from config import ADMIN_ID as _ADMIN

        if usuario.id == _ADMIN:
            await ctx.send("❌ No puedes bloquear al creador.")
            return
        if usuario.bot:
            await ctx.send("❌ No puedes bloquear a un bot.")
            return
        if await svc.add(usuario.id):
            await ctx.send(f"🚫 {usuario.mention} bloqueado de todos los comandos del bot.")
        else:
            await ctx.send(f"⚠️ {usuario.mention} ya está bloqueado.")

    @commands.command(name="unblacklist", aliases=["unbl"])
    @is_admin()
    async def unblacklist_user(
        self, ctx: commands.Context, usuario: discord.Member | None = None
    ) -> None:
        """[Admin] Desbloquea a un usuario."""
        svc = self._blacklist()
        if usuario is None:
            await ctx.send("❌ Usa: `cx!unblacklist @usuario`")
            return
        if svc is None:  # pragma: no cover
            await ctx.send("❌ Servicio de blacklist no disponible.")
            return
        if await svc.remove(usuario.id):
            await ctx.send(f"✅ {usuario.mention} desbloqueado.")
        else:
            await ctx.send(f"⚠️ {usuario.mention} no está bloqueado.")

    @commands.command(name="blacklistlist", aliases=["bllist"])
    @is_admin()
    async def blacklist_list(self, ctx: commands.Context) -> None:
        """[Admin] Lista usuarios bloqueados."""
        svc = self._blacklist()
        if svc is None:  # pragma: no cover
            await ctx.send("❌ Servicio de blacklist no disponible.")
            return
        blocked = await svc.all()
        if not blocked:
            await ctx.send("📋 No hay usuarios bloqueados.")
            return
        lines = []
        for uid in blocked:
            member = ctx.guild.get_member(int(uid)) if ctx.guild else None
            name = member.display_name if member else f"ID: {uid}"
            lines.append(f"• {name} (`{uid}`)")
        await ctx.send(
            embed=discord.Embed(
                title=f"🚫 Blacklist ({len(blocked)} usuarios)",
                description="\n".join(lines),
                color=discord.Color.red(),
            )
        )

    # -- maintenance ----------------------------------------------------
    @commands.command(name="maintenance", aliases=["mantenimiento"])
    @is_admin()
    async def maintenance_toggle(self, ctx: commands.Context) -> None:
        """[Admin] Activa/desactiva el modo mantenimiento."""
        svc = self._maintenance()
        if svc is None:  # pragma: no cover
            await ctx.send("❌ Servicio de mantenimiento no disponible.")
            return
        enabled = await svc.toggle()
        if enabled:
            embed = discord.Embed(
                title="⚙️ Modo Mantenimiento — ACTIVADO",
                description="Solo el creador puede usar comandos. El resto verá un aviso.",
                color=discord.Color.orange(),
            )
        else:
            embed = discord.Embed(
                title="⚙️ Modo Mantenimiento — DESACTIVADO",
                description="El bot vuelve a la normalidad.",
                color=discord.Color.green(),
            )
        await ctx.send(embed=embed)

    @commands.command(name="maintenance_status", aliases=["maintenancestatus", "mantstatus"])
    @is_admin()
    async def maintenance_status(self, ctx: commands.Context) -> None:
        """[Admin] Estado del modo mantenimiento."""
        svc = self._maintenance()
        enabled = await svc.is_enabled() if svc is not None else False
        await ctx.send(
            f"⚙️ Modo mantenimiento: **{'🟢 ACTIVADO' if enabled else '🔴 Desactivado'}**"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
