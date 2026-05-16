"""
GIF manager for the Teto bot.
Fetches GIFs from the Klipy API with a local fallback library.
"""
import asyncio
import logging
import random
from typing import Dict, List, Optional, Union

import aiohttp

from config import KLIPY_API_KEY, KLIPY_BASE_URL

log = logging.getLogger(__name__)

# ── Fallback GIF Library ──────────────────────────────────────────────────────
# Used when the Klipy API is unavailable or returns no results.

_FALLBACK_GIFS: Dict[str, Union[List[str], str]] = {
    "hola": [
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/18/09/67F8rUksjWt5GloTV.gif",
        "https://static.klipy.com/ii/35ccce3d852f7995dd2da910f2abd795/ab/84/gNYgJb9x.gif",
        "https://static.klipy.com/ii/8ce8357c78ea940b9c2015daf05ce1a5/8f/90/DjB67Epd.gif",
        "https://static.klipy.com/ii/c3a19a0b747a76e98651f2b9a3cca5ff/11/e2/ibW4yLT1.gif",
        "https://static.klipy.com/ii/8ce8357c78ea940b9c2015daf05ce1a5/0a/c4/ZWB0q6ej.gif",
        "https://static.klipy.com/ii/e293a233a303a98e471f78d04e13a1b0/74/b0/45Wwwv17.gif",
    ],
    "bf": [
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/6a/36/0uOGWmUeaFn1jb.gif",
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/17/17/xlNyC85ZaLUL7j.gif",
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/46/dd/WQqJpQpKYwi0bhqfh.gif",
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/0c/01/kbxB9NfhseffZ.gif",
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/0c/a0/vDx6Dlx0fx126HIA.gif",
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/1d/00/3hqWw6OHp4jYt00o5WyE.gif",
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/6d/c2/IJCwjwwp3etiDbpkLsb.gif",
    ],
    "de": [
        "https://static.klipy.com/ii/a15b48460c436e1e92c85ffc680932cc/6e/95/vLsK2pcE.gif",
        "https://static.klipy.com/ii/f87f46a2c5aeaeed4c68910815f73eaf/44/28/uf83WJLD.gif",
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/7b/cd/WYtAn08dzsWpjQtp.gif",
        "https://static.klipy.com/ii/84b4c0b02782dda9051003f9e36484ec/4a/40/AbKwTCv5.gif",
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/44/5e/rJdlt1wuhvJ5pwaIKA.gif",
        "https://static.klipy.com/ii/f87f46a2c5aeaeed4c68910815f73eaf/fa/89/4XzyJJwX.gif",
        "https://static.klipy.com/ii/e293a233a303a98e471f78d04e13a1b0/cf/b8/WWh64sR8.gif",
    ],
    "aura_high": [
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/23/36/IIdvFtTn.gif",
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/3a/8f/xG6dvEuBTbFk5s.gif",
        "https://static.klipy.com/ii/f87f46a2c5aeaeed4c68910815f73eaf/04/ff/lx7cJhef.gif",
        "https://static.klipy.com/ii/d7aec6f6f171607374b2065c836f92f4/c5/36/Fn6Mwx5L.gif",
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/0c/01/kbxB9NfhseffZ.gif",
    ],
    "aura_mid": [
        "https://static.klipy.com/ii/35ccce3d852f7995dd2da910f2abd795/83/1d/miXnBam8.gif",
        "https://static.klipy.com/ii/8ce8357c78ea940b9c2015daf05ce1a5/0a/c4/ZWB0q6ej.gif",
        "https://static.klipy.com/ii/e293a233a303a98e471f78d04e13a1b0/74/b0/45Wwwv17.gif",
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/18/09/67F8rUksjWt5GloTV.gif",
    ],
    "aura_low": [
        "https://static.klipy.com/ii/35ccce3d852f7995dd2da910f2abd795/97/e9/JqY7x9yC.gif",
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe/a1/55/eMe2oFZQ3VtMfvGKEy.gif",
        "https://i.pinimg.com/originals/63/91/26/639126a5ed46effc272235be01ad61e7.gif",
    ],
    "emergencia": (
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe"
        "/a1/55/eMe2oFZQ3VtMfvGKEy.gif"
    ),
    "alaba": [
        "https://static.klipy.com/ii/35ccce3d852f7995dd2da910f2abd795/83/1d/miXnBam8.gif",
        "https://static.klipy.com/ii/8ce8357c78ea940b9c2015daf05ce1a5/0a/c4/ZWB0q6ej.gif",
    ],
    "me": [
        "https://i.pinimg.com/originals/63/91/26/639126a5ed46effc272235be01ad61e7.gif",
    ],
}


def _get_fallback(category: str) -> str:
    """Pick a random fallback GIF from the local library."""
    pool = _FALLBACK_GIFS.get(category, _FALLBACK_GIFS["emergencia"])
    if isinstance(pool, list) and pool:
        return random.choice(pool)
    return str(pool)


async def _klipy_request(endpoint: str, params: Optional[Dict] = None) -> Optional[dict]:
    """Make a request to the Klipy API and return parsed JSON, or None on failure."""
    url = f"{KLIPY_BASE_URL}/{KLIPY_API_KEY}/{endpoint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    log.warning("Klipy API error %d for %s", resp.status, endpoint)
                    return None
                return await resp.json()
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        log.warning("Klipy API request failed: %s", e)
        return None


async def search_klipy(query: str, limit: int = 8) -> Optional[str]:
    """
    Search Klipy for a GIF matching the query.

    Args:
        query: Search term (e.g. "anime wave", "black flash").
        limit: Number of results to fetch (default 8).

    Returns:
        URL of a random matching GIF, or None if no results.
    """
    data = await _klipy_request("search", {"q": query, "limit": limit})
    if not data or not data.get("result"):
        return None

    results = data.get("data", {}).get("data", [])
    if not results:
        return None

    # Pick a random result from the pool
    chosen = random.choice(results)
    gif_url = chosen.get("file", {}).get("gif")
    if gif_url:
        # Clean escaped slashes
        gif_url = gif_url.replace("\\/", "/")
    return gif_url


async def random_klipy() -> Optional[str]:
    """Fetch a completely random GIF from Klipy."""
    data = await _klipy_request("random")
    if not data or not data.get("result"):
        return None

    gif_url = data.get("data", {}).get("file", {}).get("gif")
    if gif_url:
        gif_url = gif_url.replace("\\/", "/")
    return gif_url


async def get_giphy_gif(query: str) -> str:
    """
    Get a GIF URL based on a text query.
    Uses the curated fallback library for known anime/JJK categories,
    and falls back to Klipy API only for unknown queries.

    Args:
        query: Keywords like "hola", "black flash", "domain expansion".

    Returns:
        URL of the selected GIF.
    """
    q = query.lower()

    # ── Known categories: use curated fallback (anime/JJK content) ──
    known_categories = {
        "hola": "hola",
        "hello": "hola",
        "black flash": "bf",
        "bf": "bf",
        "domain expansion": "de",
        "de": "de",
        "alaba": "alaba",
        "glaze": "alaba",
        "me": "me",
        "teto": "me",
    }

    # Direct match for known short queries
    if q in known_categories:
        return _get_fallback(known_categories[q])

    # Check if the query contains keywords for known categories
    if "hello" in q or "hola" in q:
        return _get_fallback("hola")
    if "black flash" in q or "flash" in q:
        return _get_fallback("bf")
    if "domain" in q or "expansion" in q or "dominio" in q:
        return _get_fallback("de")
    if "alaba" in q or "glaze" in q or "praise" in q or "cumplido" in q:
        return _get_fallback("alaba")
    if "me" in q or "teto" in q:
        return _get_fallback("me")

    # ── Unknown query: try Klipy API, then emergency fallback ──
    gif_url = await search_klipy(q)
    if gif_url:
        return gif_url

    return _get_fallback("emergencia")


async def get_aura_gif(points: int) -> str:
    """
    Return a GIF URL that matches the given aura tier.
    Uses curated GIFs from the fallback library for reliable, relevant results.

    Args:
        points: Aura score.

    Returns:
        GIF URL string.
    """
    if points >= 3000:
        return _get_fallback("aura_high")
    if points >= 1000:
        return _get_fallback("aura_high")
    if points >= 0:
        return _get_fallback("aura_mid")
    return _get_fallback("aura_low")
