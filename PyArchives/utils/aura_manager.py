"""
Thread-safe manager for the Aura system.
Handles loading, saving, and scoring of aura data with asyncio locking.
"""
import json
import random
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _load_json(file_path: Path) -> Dict:
    """Load JSON data from a file safely."""
    if not file_path.exists():
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_json_atomic(data: Dict, file_path: Path) -> None:
    """Save JSON data atomically using a temporary file."""
    temp_path = file_path.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp_path.replace(file_path)


class AuraManager:
    """
    Manages aura scores with thread-safe file persistence.

    Each user gets a random daily aura value between -1000 and 5000,
    resetting every 24 hours. All mutations are protected by an asyncio.Lock.
    Compound operations (e.g. modify_aura) take the lock ONCE and perform
    read+write atomically, so concurrent callers cannot lose updates.

    Internal unlocked helpers (``_get_aura_unlocked`` / ``_set_aura_unlocked``)
    assume the caller already holds ``self._lock``. asyncio.Lock is NOT
    reentrant, so public methods and locked helpers split responsibilities.
    """

    def __init__(self, file_path: Path) -> None:
        self._file_path: Path = file_path
        self._lock: asyncio.Lock = asyncio.Lock()
        self._data: Dict = _load_json(file_path)

    # ── Internal locked helpers ────────────────────────────────────────────────

    @staticmethod
    def _today() -> int:
        """Today's day-bucket (seconds since epoch // 86400)."""
        return int(time.time() // 86400)

    def _get_aura_unlocked(self, user_id: str, today: int) -> int:
        """Read today's aura, generating it if missing. Caller holds the lock."""
        entry = self._data.get(user_id)
        if entry is None or entry.get("dia") != today:
            new_value = random.randint(-1000, 5000)
            self._data[user_id] = {"valor": new_value, "dia": today}
            _save_json_atomic(self._data, self._file_path)
            return new_value
        return entry["valor"]

    def _set_aura_unlocked(self, user_id: str, value: int, today: int) -> None:
        """Write today's aura. Caller holds the lock."""
        self._data[user_id] = {"valor": value, "dia": today}
        _save_json_atomic(self._data, self._file_path)

    # ── Public API ────────────────────────────────────────────────────────────

    async def get_aura(self, user_id: str) -> int:
        """
        Get today's aura for a user. Generates a new random value if not set today.

        Args:
            user_id: Discord user ID as string.

        Returns:
            Aura points for today.
        """
        today = self._today()
        async with self._lock:
            return self._get_aura_unlocked(user_id, today)

    async def set_aura(self, user_id: str, value: int) -> None:
        """Set a user's aura value for today."""
        today = self._today()
        async with self._lock:
            self._set_aura_unlocked(user_id, value, today)

    async def modify_aura(self, user_id: str, delta: int) -> int:
        """
        Add a delta to the user's aura and return the new value.
        Atomic: read + write happen inside a single critical section, so
        concurrent callers cannot lose updates.

        Args:
            user_id: Discord user ID as string.
            delta: Amount to add (can be negative).

        Returns:
            New aura value.
        """
        today = self._today()
        async with self._lock:
            current = self._get_aura_unlocked(user_id, today)
            new_value = current + delta
            self._set_aura_unlocked(user_id, new_value, today)
            return new_value

    async def reset_aura(self, user_id: str) -> None:
        """Remove a user's aura entry entirely."""
        async with self._lock:
            self._data.pop(user_id, None)
            _save_json_atomic(self._data, self._file_path)

    async def get_aura_if_exists(self, user_id: str) -> Optional[int]:
        """
        Get today's aura for a user if it has already been generated.
        Unlike get_aura(), this does NOT auto-generate a value if missing.

        Args:
            user_id: Discord user ID as string.

        Returns:
            Aura points for today, or None if not yet set.
        """
        today = self._today()
        async with self._lock:
            entry = self._data.get(user_id)
            if entry is not None and entry.get("dia") == today:
                return entry["valor"]
            return None

    async def get_top_aura(
        self, guild_member_ids: set, limit: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Get top aura rankings for today among the given member IDs.

        Args:
            guild_member_ids: Set of Discord user ID strings in the guild.
            limit: Max number of entries to return.

        Returns:
            List of (user_id, aura_value) tuples sorted descending.
        """
        today = self._today()
        async with self._lock:
            ranking: List[Tuple[str, int]] = []
            for uid, entry in self._data.items():
                if entry.get("dia") != today:
                    continue
                if uid in guild_member_ids:
                    ranking.append((uid, entry["valor"]))
        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking[:limit]

    # ── Static helpers ────────────────────────────────────────────────────────

    @staticmethod
    def get_aura_message(points: int) -> str:
        """Return a formatted message based on the aura tier."""
        if points >= 3000:
            return (
                f"📈 **BRUTAL.** Tienes **{points}** puntos de aura. "
                "Eres el amo del server."
            )
        if points >= 1000:
            return f"✨ Tienes **{points}** puntos de aura. Respetable."
        if points >= 0:
            return f"😐 Tienes **{points}** puntos de aura. Normalillo."
        return (
            f"📉 **{points}** puntos de aura. "
            "Tocan fondo. Mal día."
        )
