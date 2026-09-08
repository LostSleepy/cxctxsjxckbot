"""Pure parsing / formatting helpers (no discord dependency).

Centralizes logic that was duplicated or subtly inconsistent
across cogs so it can be unit-tested in isolation.
"""

from __future__ import annotations

import random
import re
import time

# ---------------------------------------------------------------------------
# Reminder durations: "10s" / "10m" / "2h" / "1d" (+ bare minutes "10")
# ---------------------------------------------------------------------------

_DURATION_RE = re.compile(r"^\s*(\d+)\s*([smhdSMHD])?\s*$")
_MULTIPLIERS = {"s": 1, "m": 60, "h": 3600, "d": 86400}

MAX_REMINDER_SECONDS = 86400


def parse_duration(raw: str | None, maximum: int = MAX_REMINDER_SECONDS) -> int | None:
    """Parse ``10s``/``10m``/``2h``/``1d`` (suffix optional, defaults to minutes).

    Returns seconds, or None when invalid / out of range (<=0 or > maximum).
    """
    if not raw:
        return None
    match = _DURATION_RE.match(raw)
    if not match:
        return None
    amount = int(match.group(1))
    suffix = (match.group(2) or "m").lower()
    seconds = amount * _MULTIPLIERS[suffix]
    if seconds <= 0 or seconds > maximum:
        return None
    return seconds


def format_duration(seconds: int) -> str:
    """Human-readable Spanish duration: 90 -> '1m 30s'."""
    if seconds < 60:
        return f"{seconds}s"
    parts: list[str] = []
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Picha measurement (deterministic per user + day)
# ---------------------------------------------------------------------------


def picha_for(user_id: int, day_bucket: int | None = None) -> tuple[int, str, str]:
    """Return (cm, bar, comment). Same user -> same result all day."""
    if day_bucket is None:
        day_bucket = int(time.time() // 86400)
    rng = random.Random(user_id + day_bucket)
    cm = rng.randint(0, 30)
    bar = "8" + "=" * cm + "D"
    if cm >= 20:
        comment = "Dios mío. 😳"
    elif cm >= 12:
        comment = "Respetable."
    elif cm >= 6:
        comment = "Normal tirando a normal."
    else:
        comment = "Hay que rezar."
    return cm, bar, comment


# ---------------------------------------------------------------------------
# Ship compatibility (deterministic per pair)
# ---------------------------------------------------------------------------


def ship_key(id_a: int, id_b: int) -> str:
    low, high = sorted((id_a, id_b))
    return f"{low}-{high}"


def ship_percent(key: str) -> int:
    """Deterministic 0-100 from a pair key (stable across restarts)."""
    rng = random.Random(f"ship:{key}")
    return rng.randint(0, 100)


def ship_bar(percent: int) -> str:
    filled = percent // 10
    return "❤️" * filled + "🖤" * (10 - filled)


# ---------------------------------------------------------------------------
# Fortnite / number formatting
# ---------------------------------------------------------------------------


def fmt_num(n: int | None) -> str:
    if n is None:
        return "—"
    return f"{n:,}".replace(",", ".")


def fmt_added(iso: str | None) -> str | None:
    """'2019-11-20T12:49:44Z' -> '20/11/2019'."""
    if not iso:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", iso)
    if not m:
        return None
    return f"{m.group(3)}/{m.group(2)}/{m.group(1)}"


# ---------------------------------------------------------------------------
# Text hygiene
# ---------------------------------------------------------------------------

_WS_RE = re.compile(r"\s+")


def clean_search(text: str, max_len: int = 100) -> str:
    """Normalize free-text search input: trim, collapse spaces, cap length."""
    return _WS_RE.sub(" ", text.strip())[:max_len]


def truncate(text: str, limit: int = 1900) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


_POKE_RE = re.compile(r"[^a-z0-9\s-]")


def normalize_pokemon(name: str) -> str:
    slug = _POKE_RE.sub("", name.strip().lower())
    return re.sub(r"\s+", "-", slug).strip("-")
