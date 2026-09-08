"""Tests for core.store (JsonStore) and services.state."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "PyArchives"))

from core.store import JsonStore, load_json_safe  # noqa: E402
from services.state import Blacklist, Maintenance, ShipStore, VoiceBan  # noqa: E402


def run(coro):
    return asyncio.run(coro)


def test_store_roundtrip(tmp_path):
    path = tmp_path / "data.json"
    store = JsonStore(path, lambda: {"a": 1})

    async def _go():
        assert await store.get() == {"a": 1}
        await store.set({"a": 2})
        assert json.loads(path.read_text(encoding="utf-8")) == {"a": 2}
        await store.update(lambda d: d.update({"b": 3}) or None)
        return await store.get()

    assert run(_go()) == {"a": 2, "b": 3}


def test_store_missing_file_uses_default(tmp_path):
    store = JsonStore(tmp_path / "nope.json", lambda: {"blocked": []})
    assert run(store.get()) == {"blocked": []}


def test_store_corrupt_file_recovers(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    store = JsonStore(path, lambda: {"ok": True})
    assert run(store.get()) == {"ok": True}
    assert (tmp_path / "bad.corrupt").exists()


def test_store_wrong_shape_recovers(tmp_path):
    path = tmp_path / "shape.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    store = JsonStore(path, lambda: {"blocked": []})
    assert run(store.get()) == {"blocked": []}


def test_store_concurrent_updates_not_lost(tmp_path):
    path = tmp_path / "c.json"
    store = JsonStore(path, lambda: {"n": 0})

    async def _go():
        async def _inc():
            def _apply(d):
                d["n"] += 1
                return None

            await store.update(_apply)

        await asyncio.gather(*(_inc() for _ in range(20)))
        return await store.get()

    assert run(_go())["n"] == 20


def test_load_json_safe(tmp_path):
    assert load_json_safe(tmp_path / "missing.json", {"d": 1}) == {"d": 1}
    bad = tmp_path / "bad.json"
    bad.write_text("xx", encoding="utf-8")
    assert load_json_safe(bad, []) == []


def test_blacklist(tmp_path):
    svc = Blacklist(tmp_path / "bl.json")

    async def _go():
        assert await svc.is_blocked(1) is False
        assert await svc.add(1) is True
        assert await svc.add(1) is False  # idempotent
        assert await svc.is_blocked(1) is True
        assert await svc.all() == ["1"]
        assert await svc.remove(1) is True
        assert await svc.remove(1) is False
        assert await svc.is_blocked(1) is False

    run(_go())


def test_maintenance_toggle(tmp_path):
    svc = Maintenance(tmp_path / "m.json")

    async def _go():
        assert await svc.is_enabled() is False
        assert await svc.toggle() is True
        assert await svc.is_enabled() is True
        assert await svc.toggle() is False

    run(_go())


def test_voiceban_toggle_and_legacy_list(tmp_path):
    path = tmp_path / "vc.json"
    svc = VoiceBan(path)

    async def _go():
        assert await svc.is_banned(7) is False
        assert await svc.toggle(7) is True
        assert await svc.is_banned(7) is True
        assert await svc.all() == ["7"]
        assert await svc.toggle(7) is False
        assert await svc.is_banned(7) is False

    run(_go())

    # Legacy bare-list file shape still loads.
    path.write_text(json.dumps(["42"]), encoding="utf-8")
    svc2 = VoiceBan(path)

    async def _go2():
        assert await svc2.is_banned(42) is True

    run(_go2())


def test_ship_store_deterministic_and_persistent(tmp_path):
    path = tmp_path / "ship.json"
    svc = ShipStore(path)

    async def _go():
        key1, pct1, cached1 = await svc.percent_for(10, 20)
        key2, pct2, cached2 = await svc.percent_for(20, 10)  # symmetric
        return (key1, pct1, cached1, key2, pct2, cached2)

    key1, pct1, cached1, key2, pct2, cached2 = run(_go())
    assert key1 == key2 == "10-20"
    assert pct1 == pct2
    assert 0 <= pct1 <= 100
    assert cached1 is False and cached2 is True
    # Persisted to disk.
    assert json.loads(path.read_text(encoding="utf-8"))["10-20"] == pct1
