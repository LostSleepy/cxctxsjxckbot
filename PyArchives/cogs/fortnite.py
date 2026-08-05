"""
Fortnite cog for the Teto Discord bot.
cx!fn — busca cosméticos de Fortnite (skins, emotes, etc.) con imagen, vídeo y
ficha completa estilo Fortnite.GG.

Fuentes (todas públicas y verificadas):
  • fortnite-api.com                → búsqueda multidioma (language=es localiza nombre/descripción)
  • fortnite.gg/api/items.json      → mapeo id oficial → id fngg (caché 24 h)
  • fortnite.gg/item-details?id=X   → ficha completa (precio, origen, wishlists, rating, vídeo)
  • fortnite-api.com/v2/shop        → tienda diaria (en español con language=es)
"""
import asyncio
import logging
import re
import time
import urllib.parse
from typing import Optional

import aiohttp
import discord
from discord.ext import commands

log = logging.getLogger(__name__)

# ── Endpoints ────────────────────────────────────────────────────────────────
FORTNITE_API_SEARCH = "https://fortnite-api.com/v2/cosmetics/br/search"
FORTNITE_API_SHOP = "https://fortnite-api.com/v2/shop"
FNGG_ITEMS_JSON = "https://fortnite.gg/api/items.json"
FNGG_ITEM_DETAILS = "https://fortnite.gg/item-details"
FNGG_IMG = "https://fortnite.gg/img/items/{}/icon.jpg"
FNGG_VIDEO = "https://fnggcdn.com/items/{}/video.mp4"

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://fortnite.gg/",
}

ITEMS_CACHE_TTL: float = 24 * 3600  # 24 h
MAX_RETRIES: int = 3
RETRY_DELAY: float = 0.8

BRAND_COLOR = discord.Color.from_rgb(255, 105, 180)


# ── Parsing helpers ─────────────────────────────────────────────────────────
def _parse_item_details(html: str) -> dict:
    """Parse the HTML fragment returned by fortnite.gg/item-details?id=."""
    data: dict = {}

    def grab(pattern: str) -> Optional[str]:
        m = re.search(pattern, html)
        return m.group(1).strip() if m else None

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


def _fmt_num(n: Optional[int]) -> str:
    """Formato español de miles: 42515 → '42.515'."""
    if n is None:
        return "—"
    return f"{n:,}".replace(",", ".")


def _fmt_added(added: Optional[str]) -> Optional[str]:
    """Convierte '2019-11-20T12:49:44Z' → '20/11/2019'."""
    if not added:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", added)
    if not m:
        return None
    return f"{m.group(3)}/{m.group(2)}/{m.group(1)}"


# ── Traducciones ES (valores que fngg devuelve en inglés) ───────────────────
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


# ── Cog ──────────────────────────────────────────────────────────────────────
class Fortnite(commands.Cog):
    """Comandos de Fortnite: cx!fn <nombre> / video / shop."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._session: Optional[aiohttp.ClientSession] = None
        self._items_cache: Optional[dict] = None
        self._items_cache_ts: float = 0.0
        self._items_lock: asyncio.Lock = asyncio.Lock()

    async def cog_unload(self) -> None:
        """Close the aiohttp session when the cog is unloaded."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _fetch(
        self, url: str, browser: bool = False, is_json: bool = True
    ) -> Optional[object]:
        """Fetch JSON or text with error handling and retries (fngg es intermitente con Cloudflare)."""
        last_error = ""
        for attempt in range(MAX_RETRIES):
            try:
                session = await self._get_session()
                headers = BROWSER_HEADERS if browser else None
                async with session.get(
                    url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    if resp.status != 200:
                        last_error = f"HTTP {resp.status}"
                    elif is_json:
                        return await resp.json()
                    else:
                        text = await resp.text()
                        # Detectar el reto de Cloudflare (200 pero sin datos reales)
                        if browser and "challenge-body-text" in text and "fn-detail" not in text:
                            last_error = "Cloudflare challenge"
                        else:
                            return text
            except Exception as e:
                last_error = str(e)
            log.warning(
                "Intento %d/%d fallido en %s: %s",
                attempt + 1, MAX_RETRIES, url, last_error,
            )
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
        log.error("Fetch fallido tras %d intentos: %s (%s)", MAX_RETRIES, url, last_error)
        return None

    # ── Búsqueda multidioma (es → en → contains) ────────────────────────────
    async def _search_cosmetic(self, query: str):
        """Busca un cosmético por nombre en cualquier idioma.

        Devuelve (cosmético, idioma) — 'es' si se encontró por nombre en
        español, 'en' en caso contrario.
        """
        q = query.strip()
        variants = [
            ({"name": q, "searchLanguage": "es", "language": "es"}, "es"),
            ({"name": q}, "en"),
            ({"name": q, "matchMethod": "contains", "matchFields": "name"}, "en"),
        ]
        for params, lang in variants:
            url = f"{FORTNITE_API_SEARCH}?{urllib.parse.urlencode(params)}"
            data = await self._fetch(url)
            if not data or data.get("status") != 200:
                continue
            result = data.get("data")
            if isinstance(result, list):
                result = result[0] if result else None
            if isinstance(result, dict) and result.get("id"):
                return result, lang
        return None, None

    # ── Fortnite.GG: id fngg (caché 24 h) ───────────────────────────────────
    async def _get_fngg_id(self, fortnite_id: str) -> Optional[str]:
        """Mapea el id oficial de Fortnite al id interno de Fortnite.GG (caché 24 h)."""
        async with self._items_lock:
            now = time.time()
            if self._items_cache is None or now - self._items_cache_ts > ITEMS_CACHE_TTL:
                data = await self._fetch(FNGG_ITEMS_JSON, browser=True)
                if isinstance(data, dict) and data:
                    self._items_cache = data
                    self._items_cache_ts = now
                    log.info("items.json cacheado (%d ítems)", len(data))
        if self._items_cache:
            return self._items_cache.get(fortnite_id)
        return None

    # ── Fortnite.GG: ficha completa del ítem ────────────────────────────────
    async def _get_item_details(self, fngg_id: int) -> Optional[dict]:
        """Ficha estilo Fortnite.GG (precio, origen, wishlists, rating, vídeo)."""
        html = await self._fetch(
            f"{FNGG_ITEM_DETAILS}?id={fngg_id}", browser=True, is_json=False
        )
        if not html:
            return None
        return _parse_item_details(html)

    def _error_embed(self, title: str, description: str) -> discord.Embed:
        """Embed de error estándar."""
        return discord.Embed(title=title, description=description, color=discord.Color.red())

    # ── Embed de info estilo Fortnite.GG ────────────────────────────────────
    async def _send_info(self, ctx: commands.Context, query: str) -> None:
        """Embed completo con imagen del baile + datos de Fortnite.GG."""
        async with ctx.typing():
            cosmetic, lang = await self._search_cosmetic(query)
            if not cosmetic:
                embed = self._error_embed(
                    "❌ Cosmético no encontrado",
                    f"No encontré **{query}**. Prueba con otro nombre, también vale en español.",
                )
                await ctx.send(embed=embed)
                return

            cid = cosmetic.get("id", "")
            fngg_id = await self._get_fngg_id(cid)
            details = await self._get_item_details(int(fngg_id)) if fngg_id else None
            details_failed = details is None
            if details is None:
                details = {}

            # Nombre y descripción localizados (language=es en la búsqueda)
            if lang == "es":
                name = cosmetic.get("name") or details.get("name") or query.title()
            else:
                name = details.get("name") or cosmetic.get("name", query.title())
            rarity = details.get("rarity") or cosmetic.get(
                "rarity", {}
            ).get("displayValue", "?")
            ctype = details.get("type") or cosmetic.get("type", {}).get(
                "displayValue", "?"
            )
            if lang == "es":
                rarity = RARITY_ES.get(rarity, rarity)
                ctype = TYPE_ES.get(ctype, ctype)
            if lang == "es":
                desc = cosmetic.get("description") or details.get("description") or None
            else:
                desc = details.get("description") or cosmetic.get("description") or None

            intro = cosmetic.get("introduction") or {}
            chapter = intro.get("chapter")
            if chapter:
                introduced = f"Capítulo {chapter}, Temporada {intro.get('season', '?')}"
            else:
                introduced = details.get("introduced") or "—"

            if lang == "es":
                release = _fmt_added(cosmetic.get("added")) or details.get("release") or "—"
            else:
                release = details.get("release") or _fmt_added(cosmetic.get("added")) or "—"
            set_name = cosmetic.get("set", {}).get("value") or details.get("set")
            price = details.get("price")
            source = details.get("source")
            if lang == "es" and source:
                source = SOURCE_ES.get(source, source)
            collab = details.get("collab")

            embed = discord.Embed(
                title=f"{name} — {rarity} • {ctype}",
                description=desc,
                color=BRAND_COLOR,
            )

            # Imagen del baile (icono de fngg, fallback al render oficial)
            img_url = FNGG_IMG.format(fngg_id) if fngg_id else None
            if not img_url:
                img_url = cosmetic.get("images", {}).get("icon")
            if img_url:
                embed.set_image(url=img_url)

            if price:
                embed.add_field(name="💰 Precio", value=price, inline=True)
            if source:
                embed.add_field(name="🏷️ Origen", value=source, inline=True)
            if introduced:
                embed.add_field(name="📅 Introducido en", value=introduced, inline=True)
            if release:
                embed.add_field(name="🗓️ Fecha de lanzamiento", value=release, inline=True)
            if set_name:
                embed.add_field(name="📦 Set", value=set_name, inline=True)
            if collab:
                embed.add_field(name="🤝 Colab", value=collab, inline=True)

            wishlists = details.get("wishlists")
            if wishlists is not None:
                embed.add_field(name="💖 Wishlists", value=_fmt_num(wishlists), inline=True)
            rating = details.get("rating")
            votes = details.get("votes")
            if rating is not None and votes:
                embed.add_field(
                    name="⭐ Valoración",
                    value=f"{rating}% ({_fmt_num(votes)} votos)",
                    inline=True,
                )

            # Enlace al vídeo del baile (se reproduce con cx!fn video).
            # Solo se construye la URL a mano si falló la ficha (no si el ítem no tiene vídeo).
            video = details.get("video")
            if not video and details_failed and fngg_id:
                video = FNGG_VIDEO.format(fngg_id)
            if video:
                clean_video = video.split("?")[0]  # quitar cache-buster (?4) para Discord
                embed.add_field(
                    name="🎬 Baile",
                    value=f"[Ver el vídeo]({clean_video}) · o usa `cx!fn video {name}`",
                    inline=False,
                )

            embed.add_field(name="🆔 ID", value=f"`{cid}`", inline=False)
            embed.set_footer(
                text="Fortnite-API + Fortnite.GG",
                icon_url=ctx.author.display_avatar.url,
            )

        await ctx.send(embed=embed)

    # ── Comandos ────────────────────────────────────────────────────────────
    @commands.group(name="fn", aliases=["fortnite"], invoke_without_command=True)
    async def fn(self, ctx: commands.Context, *, query: Optional[str] = None) -> None:
        """🎮 Cosmético de Fortnite: cx!fn <nombre> / video / shop."""
        if not query:
            embed = discord.Embed(
                title="🎮 cx!fn — Fortnite",
                description=(
                    "Busca skins, emotes y más con ficha estilo Fortnite.GG.\n\n"
                    "`cx!fn <nombre>` — Ficha completa con imagen (precio, origen, wishlists, rating)\n"
                    "`cx!fn video <nombre>` — Vídeo del baile 🎬\n"
                    "`cx!fn shop` — Tienda de hoy 🛒\n\n"
                    "Acepta nombres en español: `cx!fn video escenario`."
                ),
                color=BRAND_COLOR,
            )
            await ctx.send(embed=embed)
            return
        await self._send_info(ctx, query)

    @fn.command(name="video", aliases=["v"])
    async def fn_video(self, ctx: commands.Context, *, query: str) -> None:
        """🎬 Envía el enlace al vídeo del baile (Discord lo reproduce)."""
        async with ctx.typing():
            cosmetic, _lang = await self._search_cosmetic(query)
            if not cosmetic:
                await ctx.send(
                    embed=self._error_embed(
                        "❌ Cosmético no encontrado", f"No encontré **{query}**."
                    )
                )
                return

            fngg_id = await self._get_fngg_id(cosmetic.get("id", ""))
            video = None
            if fngg_id:
                details = await self._get_item_details(int(fngg_id))
                if details is not None and details.get("video"):
                    video = details["video"]
                elif details is None:
                    video = FNGG_VIDEO.format(fngg_id)

            if not video:
                await ctx.send(
                    embed=self._error_embed(
                        "❌ Sin vídeo",
                        f"**{cosmetic.get('name', query)}** no tiene vídeo disponible.",
                    )
                )
                return

            await ctx.send(video.split("?")[0])

    @fn.command(name="shop", aliases=["tienda"])
    async def fn_shop(self, ctx: commands.Context) -> None:
        """🛒 Tienda diaria de Fortnite."""
        async with ctx.typing():
            data = await self._fetch(f"{FORTNITE_API_SHOP}?language=es")
            if not data or data.get("status") != 200:
                await ctx.send(
                    embed=self._error_embed(
                        "❌ Error", "No pude obtener la tienda de hoy."
                    )
                )
                return

            entries = data.get("data", {}).get("entries", [])
            date = (data.get("data", {}).get("date") or "")[:10]
            parts = date.split("-")
            date_es = f"{parts[2]}/{parts[1]}/{parts[0]}" if len(parts) == 3 else date

            # La tienda viene en español gracias a language=es
            rows = []
            for entry in entries[:12]:
                br = (entry.get("brItems") or [{}])[0]
                name = br.get("name") or entry.get("devName", "?")
                price = entry.get("finalPrice") or entry.get("regularPrice")
                price_str = f"{price} V-Bucks" if price is not None else "—"
                rows.append(f"• **{name}** — {price_str}")

            embed = discord.Embed(
                title="🛒 Tienda de hoy" + (f" ({date_es})" if date_es else ""),
                description="\n".join(rows),
                color=BRAND_COLOR,
            )
            embed.add_field(
                name="Total de ofertas",
                value=str(len(entries)),
                inline=True,
            )
            embed.add_field(
                name="ℹ️",
                value=f"Usa `cx!fn <nombre>` para la ficha de uno de estos {len(entries)} ítems.",
                inline=True,
            )
            embed.set_footer(
                text="Fortnite-API",
                icon_url=ctx.author.display_avatar.url,
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Load the Fortnite cog."""
    await bot.add_cog(Fortnite(bot))
