"""Consistent embed builders — one visual language for the whole bot."""

from __future__ import annotations

import discord

BRAND = discord.Color.from_rgb(255, 105, 180)
GOLD = discord.Color.gold()
GREEN = discord.Color.green()
RED = discord.Color.red()
ORANGE = discord.Color.orange()
BLUE = discord.Color.blue()
GREY = discord.Color.dark_grey()


def _footer(embed: discord.Embed, ctx) -> discord.Embed:
    try:
        embed.set_footer(
            text=f"Solicitado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )
    except Exception:
        pass
    return embed


def ok(title: str, description: str, ctx=None) -> discord.Embed:
    e = discord.Embed(title=title, description=description, color=GREEN)
    return _footer(e, ctx) if ctx else e


def error(title: str, description: str, ctx=None) -> discord.Embed:
    e = discord.Embed(title=title, description=description, color=RED)
    return _footer(e, ctx) if ctx else e


def info(
    title: str, description: str, color: discord.Color | None = None, ctx=None
) -> discord.Embed:
    e = discord.Embed(title=title, description=description, color=color or BLUE)
    return _footer(e, ctx) if ctx else e


def brand(title: str, description: str, ctx=None) -> discord.Embed:
    e = discord.Embed(title=title, description=description, color=BRAND)
    return _footer(e, ctx) if ctx else e
