"""Atomic JSON store with asyncio locking.

Replaces the ad-hoc ``load json / dump json`` blocks scattered
across cogs. One class, one behaviour:

* missing file -> default
* corrupt file -> default (and the corrupt file is preserved as ``.corrupt``)
* writes are atomic (tmp + replace) and serialized by an asyncio lock
* read-modify-write via :meth:`update` is atomic for concurrent commands
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

log = logging.getLogger(__name__)

T = TypeVar("T")


class JsonStore:
    def __init__(
        self, path: Path, default: Callable[[], T], coerce: Callable[[Any], T | None] | None = None
    ) -> None:
        self._path = path
        self._default = default
        self._coerce = coerce
        self._lock = asyncio.Lock()
        self._data: T = self._load()

    # -- sync load (called once at startup; file is tiny) --
    def _load(self) -> T:
        if not self._path.exists():
            return self._default()
        try:
            with open(self._path, encoding="utf-8") as f:
                loaded = json.load(f)
            # Guard against valid JSON of the wrong shape (e.g. list vs dict).
            default = self._default()
            if isinstance(default, dict) and not isinstance(loaded, dict):
                raise ValueError("shape mismatch")
            if isinstance(default, list) and not isinstance(loaded, list):
                raise ValueError("shape mismatch")
            return loaded
        except (json.JSONDecodeError, OSError, ValueError, UnicodeDecodeError) as e:
            coerced = self._try_coerce()
            if coerced is not None:
                return coerced
            log.warning(
                "Datos corruptos en %s (%s); usando valores por defecto.", self._path.name, e
            )
            try:
                corrupt = self._path.with_suffix(".corrupt")
                if self._path.exists():
                    self._path.replace(corrupt)
            except OSError:
                pass
            return self._default()

    def _try_coerce(self) -> T | None:
        """Try to migrate legacy file shapes instead of discarding them."""
        if self._coerce is None:
            return None
        try:
            with open(self._path, encoding="utf-8") as f:
                loaded = json.load(f)
            result = self._coerce(loaded)
            if result is not None:
                self._data = result
                self._save_unlocked()
                log.info("Migrado formato legacy en %s.", self._path.name)
                return result
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            pass
        except Exception as e:  # pragma: no cover - defensive
            log.warning("Coerce falló en %s: %s", self._path.name, e)
        return None

    def _save_unlocked(self) -> None:
        tmp = self._path.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            tmp.replace(self._path)
        except OSError as e:
            log.error("No se pudo guardar %s: %s", self._path.name, e)

    @property
    def path(self) -> Path:
        return self._path

    async def get(self) -> T:
        async with self._lock:
            return self._data

    async def set(self, value: T) -> None:
        async with self._lock:
            self._data = value
            self._save_unlocked()

    async def update(self, fn: Callable[[T], T | None]) -> T:
        """Apply ``fn`` to the stored value atomically.

        If ``fn`` returns None the data is left untouched (but the
        in-place mutation, if any, is still persisted).
        Async callbacks are also accepted (and awaited).
        """
        import inspect

        async with self._lock:
            result = fn(self._data)
            if inspect.isawaitable(result):
                result = await result
            if result is not None:
                self._data = result
            self._save_unlocked()
            return self._data

    async def reload(self) -> T:
        async with self._lock:
            self._data = self._load()
            return self._data


def load_json_safe(path: Path, default: Any) -> Any:
    """One-shot safe load for tiny read-only uses (diagnostics, backup)."""
    if not path.exists():
        return default
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return default
