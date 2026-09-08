"""Shared aiohttp client with timeouts and retries.

All API cogs MUST use this instead of creating their own
``ClientSession`` per request (the old code created a session
per dictionary lookup and leaked sessions on reload).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

log = logging.getLogger(__name__)

_session = None
_lock: asyncio.Lock | None = None


def _get_lock() -> asyncio.Lock:
    global _lock
    if _lock is None:
        _lock = asyncio.Lock()
    return _lock


async def get_session():
    """Process-wide shared session (created lazily, reused everywhere)."""
    global _session
    import aiohttp

    if _session is None or _session.closed:
        async with _get_lock():
            if _session is None or _session.closed:
                timeout = aiohttp.ClientTimeout(total=12)
                headers = {"User-Agent": "TetoDiscordBot/2.0 (+discord.py)"}
                _session = aiohttp.ClientSession(timeout=timeout, headers=headers)
    return _session


async def close_session() -> None:
    global _session
    if _session is not None and not _session.closed:
        try:
            await _session.close()
        except Exception:
            pass
    _session = None


async def fetch_json(url: str, *, retries: int = 2, backoff: float = 0.6) -> Any | None:
    """GET JSON with a couple of retries. Returns None on any failure."""
    import aiohttp

    last: str = ""
    for attempt in range(retries + 1):
        try:
            session = await get_session()
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                if resp.status in (404, 400, 422):
                    return None  # no point retrying client errors
                last = f"HTTP {resp.status}"
        except (TimeoutError, aiohttp.ClientError) as e:
            last = str(e)
        except Exception as e:  # pragma: no cover - defensive
            log.error("fetch_json %s: %s", url, e)
            return None
        if attempt < retries:
            await asyncio.sleep(backoff * (attempt + 1))
    log.warning("fetch_json falló %s (%s)", url, last)
    return None


async def fetch_text(url: str, *, headers: dict | None = None, retries: int = 2) -> str | None:
    import aiohttp

    for attempt in range(retries + 1):
        try:
            session = await get_session()
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.text()
                if resp.status in (404, 400, 422):
                    return None
        except (TimeoutError, aiohttp.ClientError):
            pass
        except Exception:  # pragma: no cover - defensive
            return None
        if attempt < retries:
            await asyncio.sleep(0.6 * (attempt + 1))
    return None
