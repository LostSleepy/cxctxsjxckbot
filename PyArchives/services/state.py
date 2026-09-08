"""Persistent bot state backed by JsonStore.

One place for blacklist / maintenance / voice-ban / ship data.
Cogs inject these instead of doing file I/O inline, which fixes
the race conditions of the old load-modify-save-per-command code.
"""

from __future__ import annotations

from pathlib import Path

from core.parsing import ship_key, ship_percent
from core.store import JsonStore


class Blacklist:
    def __init__(self, path: Path) -> None:
        self._store = JsonStore(path, lambda: {"blocked": []})

    async def is_blocked(self, user_id: int) -> bool:
        data = await self._store.get()
        return str(user_id) in set(data.get("blocked", []))

    async def add(self, user_id: int) -> bool:
        uid = str(user_id)
        data = await self._store.get()
        blocked = set(data.get("blocked", []))
        if uid in blocked:
            return False
        blocked.add(uid)

        def _apply(d):
            d["blocked"] = sorted(blocked)
            return None

        await self._store.update(_apply)
        return True

    async def remove(self, user_id: int) -> bool:
        uid = str(user_id)
        data = await self._store.get()
        blocked = set(data.get("blocked", []))
        if uid not in blocked:
            return False
        blocked.discard(uid)

        def _apply(d):
            d["blocked"] = sorted(blocked)
            return None

        await self._store.update(_apply)
        return True

    async def all(self) -> list[str]:
        data = await self._store.get()
        return sorted(data.get("blocked", []))


class Maintenance:
    def __init__(self, path: Path) -> None:
        self._store = JsonStore(path, lambda: {"enabled": False})

    async def is_enabled(self) -> bool:
        return bool((await self._store.get()).get("enabled", False))

    async def toggle(self) -> bool:
        def _apply(d):
            d["enabled"] = not d.get("enabled", False)
            return None

        data = await self._store.update(_apply)
        return bool(data.get("enabled", False))


class VoiceBan:
    def __init__(self, path: Path) -> None:
        def _coerce(loaded):
            # Legacy shape: bare list of IDs.
            if isinstance(loaded, list):
                return {"banned": sorted({str(x) for x in loaded})}
            return None

        self._store = JsonStore(path, lambda: {"banned": []}, coerce=_coerce)

    async def _ids(self) -> set[str]:
        data = await self._store.get()
        if isinstance(data, list):
            return {str(x) for x in data}
        return {str(x) for x in data.get("banned", [])}

    async def is_banned(self, user_id: int) -> bool:
        return str(user_id) in await self._ids()

    async def toggle(self, user_id: int) -> bool:
        """Toggle; returns True if the user is now banned."""
        uid = str(user_id)
        ids = await self._ids()
        if uid in ids:
            ids.discard(uid)
            banned = False
        else:
            ids.add(uid)
            banned = True

        def _apply(d):
            if isinstance(d, list):
                return {"banned": sorted(ids)}
            d["banned"] = sorted(ids)
            return None

        await self._store.update(_apply)
        return banned

    async def all(self) -> list[str]:
        return sorted(await self._ids())


class ShipStore:
    """Persistent ship percentages keyed by sorted pair 'low-high'."""

    def __init__(self, path: Path) -> None:
        self._store = JsonStore(path, lambda: {})

    async def percent_for(self, id_a: int, id_b: int) -> tuple[str, int, bool]:
        """Return (key, percent, cached). Generates + persists on first ship."""
        key = ship_key(id_a, id_b)
        data = await self._store.get()
        if key in data:
            try:
                return key, int(data[key]), True
            except (TypeError, ValueError):
                pass
        percent = ship_percent(key)

        def _apply(d):
            d[key] = percent
            return None

        await self._store.update(_apply)
        return key, percent, False
