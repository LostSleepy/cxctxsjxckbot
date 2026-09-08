"""Pure Fortnite helpers (no discord/aiohttp dependency).

Extracted from the Fortnite cog so the HTML parsing and
formatting logic can be unit-tested without discord.py.
"""

from __future__ import annotations

import re

FNGG_VIDEO = "https://fnggcdn.com/items/{}/video.mp4"


def video_url(fngg_id: str) -> str:
    return FNGG_VIDEO.format(fngg_id)


def youtube_url(cosmetic: dict) -> str | None:
    yt_id = cosmetic.get("showcaseVideo")
    if yt_id:
        return f"https://youtu.be/{yt_id}"
    return None


def parse_item_details(html: str) -> dict:
    """Parse the HTML fragment returned by fortnite.gg/item-details?id=."""

    def grab(pattern: str) -> str | None:
        m = re.search(pattern, html)
        return m.group(1).strip() if m else None

    data: dict = {}
    data["name"] = grab(r"fn-detail-name'>([^<]+)</div>")
    data["rarity"] = grab(r"fn-detail-type'><span[^>]*>([^<]+)</span>")
    data["type"] = grab(r"fn-detail-type'><span[^>]*>[^<]+</span>\s*([^<]+)</div>")
    data["price"] = grab(r"fn-item-price'>([^<]*)</div>")
    data["description"] = grab(r"fn-detail-desc[^>]*>([^<]+)</div>")
    data["source"] = grab(r">Source:</th><td>(?:<a[^>]*>)?([^<]+)")
    data["introduced"] = grab(r">Introduced in:</th><td>(?:<a[^>]*>)?([^<]+)")
    data["release"] = grab(r">Release date:</th><td>([^<]+)</td>")
    data["collab"] = grab(r">Collab:</th><td>(?:<a[^>]*>)?([^<]+)")

    m = re.search(r"data-type='wishlist'[^>]*>.*?data-n='(\d+)'", html, re.S)
    data["wishlists"] = int(m.group(1)) if m else None

    m = re.search(r"data-total='(\d+)' data-sum='(\d+)'", html)
    if m:
        total, ssum = int(m.group(1)), int(m.group(2))
        data["votes"] = total
        data["rating"] = round(ssum / (total * 4) * 100) if total else None
    else:
        data["votes"] = None
        data["rating"] = None

    m = re.search(r"src='(https://fnggcdn\.com/items/\d+/video\.mp4[^']*)'", html)
    data["video"] = m.group(1) if m else None

    return data


def fmt_num(n: int | None) -> str:
    if n is None:
        return "—"
    return f"{n:,}".replace(",", ".")


def fmt_added(added: str | None) -> str | None:
    """'2019-11-20T12:49:44Z' -> '20/11/2019'."""
    if not added:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", added)
    if not m:
        return None
    return f"{m.group(3)}/{m.group(2)}/{m.group(1)}"


SOURCE_ES = {
    "Shop": "Tienda",
    "Battle Pass": "Pase de batalla",
    "Crew": "Tripulación",
    "Challenges": "Desafíos",
    "Exclusives": "Exclusivo",
    "Packs": "Paquetes",
    "OG Pass": "Pase OG",
    "Music Pass": "Pase de Música",
    "Lego Pass": "Pase Lego",
    "Tournaments": "Torneos",
}

RARITY_ES = {
    "Common": "Común",
    "Uncommon": "Poco común",
    "Rare": "Raro",
    "Epic": "Épico",
    "Legendary": "Legendario",
    "Icon Series": "Serie Icono",
    "Marvel Series": "Serie Marvel",
    "DC Series": "Serie DC",
    "Star Wars Series": "Serie Star Wars",
    "Gaming Legends Series": "Serie Leyendas de Gaming",
    "Crew Pack": "Pack de Tripulación",
}

TYPE_ES = {
    "Outfit": "Traje",
    "Emote": "Emote",
    "Pickaxe": "Pico",
    "Backpack": "Mochila",
    "Glider": "Planeador",
    "Wrap": "Envoltura",
    "Contrail": "Estela",
    "Spray": "Spray",
    "Emoji": "Emoji",
    "Loading Screen": "Pantalla de carga",
    "Music": "Música",
    "Bundle": "Pack",
    "Car": "Coche",
    "Decal": "Diseño",
    "Wheels": "Ruedas",
    "Kicks": "Zapatillas",
    "Jam Track": "Tema musical",
    "Instrument": "Instrumento",
    "Banner": "Estandarte",
    "Toy": "Juguete",
    "Trail": "Estela",
    "Boost": "Impulso",
    "Aura": "Aura",
    "Sidekick": "Acompañante",
}
