"""
GIF manager for the Teto bot.
Provides themed GIF URLs for various commands and events.
"""
import random
from typing import Dict, List, Union

# ── GIF Library ────────────────────────────────────────────────────────────────

_GIF_LIBRARY: Dict[str, Union[List[str], str]] = {
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
    "emergencia": (
        "https://static.klipy.com/ii/4e7bea9f7a3371424e6c16ebc93252fe"
        "/a1/55/eMe2oFZQ3VtMfvGKEy.gif"
    ),
}


async def get_giphy_gif(query: str) -> str:
    """
    Select a random GIF based on a text query.

    Args:
        query: Keywords like "hola", "black flash", "domain expansion".

    Returns:
        URL of the selected GIF.
    """
    q = query.lower()
    emergencia: str = _GIF_LIBRARY["emergencia"]  # type: ignore[assignment]

    if "hello" in q or "hola" in q:
        pool = _GIF_LIBRARY.get("hola", [])
    elif "black flash" in q:
        pool = _GIF_LIBRARY.get("bf", [])
    elif "domain" in q or "expansion" in q:
        pool = _GIF_LIBRARY.get("de", [])
    else:
        return emergencia

    if isinstance(pool, list) and pool:
        return random.choice(pool)
    return emergencia
