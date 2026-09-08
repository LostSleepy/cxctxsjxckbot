"""Shared command checks (Discord-dependent)."""

from __future__ import annotations

from discord.ext import commands

from core.settings import ADMIN_ID


def is_admin() -> commands.check:
    """Allow the configured admin (and any Discord app owner)."""

    async def predicate(ctx: commands.Context) -> bool:
        if ctx.author.id == ADMIN_ID:
            return True
        try:
            if await ctx.bot.is_owner(ctx.author):
                return True
        except Exception:
            pass
        raise commands.CheckFailure("Solo el creador puede usar este comando.")

    return commands.check(predicate)


async def admin_bypass_cooldown(ctx: commands.Context) -> None:
    """Reset the current command cooldown for the admin (no-op otherwise)."""
    try:
        if ctx.author.id == ADMIN_ID or await ctx.bot.is_owner(ctx.author):
            if ctx.command is not None:
                ctx.command.reset_cooldown(ctx)
    except Exception:
        pass


def in_guild() -> commands.check:
    """Require the command to run inside a server (not DMs)."""

    async def predicate(ctx: commands.Context) -> bool:
        if ctx.guild is None:
            raise commands.NoPrivateMessage("Este comando no funciona en DMs.")
        return True

    return commands.check(predicate)


def bot_can_moderate_members(ctx: commands.Context) -> bool:
    me = ctx.guild.me if ctx.guild else None
    return bool(me is not None and me.guild_permissions.moderate_members)
