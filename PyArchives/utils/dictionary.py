"""
Dictionary lookup utility for the Teto Discord bot.
Uses the FreeDictionaryAPI (https://api.dictionaryapi.dev/) for real definitions.
Supports both Spanish and English words.
"""
import asyncio
import logging
from typing import Optional

import aiohttp

log = logging.getLogger(__name__)

DICT_API_BASE = "https://api.dictionaryapi.dev/api/v2/entries"


async def lookup_word(word: str) -> Optional[list[str]]:
    """Look up a word in the dictionary. Returns list of definitions or None.

    Tries Spanish first, then English.
    """
    word = word.strip().lower()

    # Try Spanish first
    definitions = await _fetch_definitions(word, "es")
    if definitions:
        return definitions

    # Fall back to English
    definitions = await _fetch_definitions(word, "en")
    if definitions:
        return definitions

    return None


async def _fetch_definitions(word: str, lang: str) -> Optional[list[str]]:
    """Fetch definitions from the FreeDictionaryAPI for a given language."""
    url = f"{DICT_API_BASE}/{lang}/{word}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None

                data = await resp.json()
                if not data or not isinstance(data, list):
                    return None

                definitions: list[str] = []
                for entry in data:
                    if "meanings" in entry:
                        for meaning in entry["meanings"]:
                            part_of_speech = meaning.get("partOfSpeech", "")
                            for def_item in meaning.get("definitions", []):
                                definition = def_item.get("definition", "")
                                if definition:
                                    prefix = f"({part_of_speech}) " if part_of_speech else ""
                                    definitions.append(f"{prefix}{definition}")

                return definitions[:5]  # Max 5 definitions
    except asyncio.TimeoutError:
        log.warning("Dictionary API timeout for word '%s' (%s)", word, lang)
        return None
    except Exception as e:
        log.error("Dictionary API error for word '%s' (%s): %s", word, lang, e)
        return None
