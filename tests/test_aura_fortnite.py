"""Tests for AuraManager, gif tiers and fortnite pure parsers."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "PyArchives"))

from core.fortnite_parse import (  # noqa: E402
    RARITY_ES,
    SOURCE_ES,
    TYPE_ES,
    fmt_added,
    fmt_num,
    parse_item_details,
    video_url,
    youtube_url,
)
from utils.aura_manager import AuraManager  # noqa: E402
from utils.gif_manager import get_aura_gif, get_giphy_gif  # noqa: E402


def run(coro):
    return asyncio.run(coro)


# -- AuraManager ------------------------------------------------------------


def test_aura_generates_in_range_and_is_stable(tmp_path):
    mgr = AuraManager(tmp_path / "aura.json")

    async def _go():
        first = await mgr.get_aura("123")
        second = await mgr.get_aura("123")
        return first, second

    first, second = run(_go())
    assert -1000 <= first <= 5000
    assert first == second  # stable within the same day


def test_aura_set_modify_reset(tmp_path):
    mgr = AuraManager(tmp_path / "aura.json")

    async def _go():
        await mgr.set_aura("u", 100)
        assert await mgr.get_aura("u") == 100
        assert await mgr.modify_aura("u", 50) == 150
        assert await mgr.modify_aura("u", -200) == -50
        await mgr.reset_aura("u")
        assert await mgr.get_aura_if_exists("u") is None

    run(_go())


def test_aura_if_exists_does_not_generate(tmp_path):
    mgr = AuraManager(tmp_path / "aura.json")

    async def _go():
        assert await mgr.get_aura_if_exists("ghost") is None
        # Still missing afterwards (no side effect).
        assert await mgr.get_aura_if_exists("ghost") is None

    run(_go())


def test_aura_concurrent_modify_not_lost(tmp_path):
    mgr = AuraManager(tmp_path / "aura.json")

    async def _go():
        await mgr.set_aura("u", 0)
        await asyncio.gather(*(mgr.modify_aura("u", 10) for _ in range(10)))
        return await mgr.get_aura("u")

    assert run(_go()) == 100


def test_aura_rolls_over_next_day(tmp_path, monkeypatch):
    import time as _time

    mgr = AuraManager(tmp_path / "aura.json")
    day_one = 20000 * 86400 + 100

    async def _go():
        monkeypatch.setattr(_time, "time", lambda: day_one)
        await mgr.set_aura("u", 111)
        assert await mgr.get_aura("u") == 111
        # Next day: stored entry is stale -> fresh random value.
        monkeypatch.setattr(_time, "time", lambda: day_one + 86401)
        assert await mgr.get_aura_if_exists("u") is None
        fresh = await mgr.get_aura("u")
        assert -1000 <= fresh <= 5000

    run(_go())


def test_aura_message_tiers():
    assert "BRUTAL" in AuraManager.get_aura_message(3000)
    assert "Respetable" in AuraManager.get_aura_message(1000)
    assert "Normalillo" in AuraManager.get_aura_message(0)
    assert "Mal día" in AuraManager.get_aura_message(-1)


def test_aura_top_filters_and_limits(tmp_path):
    mgr = AuraManager(tmp_path / "aura.json")

    async def _go():
        await mgr.set_aura("1", 100)
        await mgr.set_aura("2", 900)
        await mgr.set_aura("3", 500)
        await mgr.set_aura("outsider", 9999)
        return await mgr.get_top_aura({"1", "2", "3"}, limit=2)

    top = run(_go())
    assert [uid for uid, _ in top] == ["2", "3"]  # sorted desc, outsider excluded


# -- GIF tiers --------------------------------------------------------------


def test_aura_gif_tiers():
    async def _go():
        high = await get_aura_gif(3000)
        mid = await get_aura_gif(100)
        low = await get_aura_gif(-5)
        assert isinstance(high, str) and high.startswith("http")
        assert isinstance(mid, str) and mid.startswith("http")
        assert isinstance(low, str) and low.startswith("http")
        assert len({high, mid, low}) == 3  # distinct tier per category

    run(_go())


def test_giphy_known_and_unknown_queries():
    async def _go():
        hola = await get_giphy_gif("hola")
        bf = await get_giphy_gif("black flash")
        de = await get_giphy_gif("domain expansion")
        unknown = await get_giphy_gif("zzz-no-existe-zzz")
        for gif in (hola, bf, de, unknown):
            assert isinstance(gif, str) and gif.startswith("http")

    run(_go())


# -- Fortnite parsers -------------------------------------------------------


def test_fortnite_fmt_helpers():
    assert fmt_num(42515) == "42.515"
    assert fmt_num(None) == "—"
    assert fmt_added("2019-11-20T12:49:44Z") == "20/11/2019"
    assert fmt_added(None) is None
    assert fmt_added("bogus") is None


def test_fortnite_urls():
    assert video_url("123") == "https://fnggcdn.com/items/123/video.mp4"
    assert youtube_url({"showcaseVideo": "abc"}) == "https://youtu.be/abc"
    assert youtube_url({}) is None


def test_fortnite_parse_empty_html():
    data = parse_item_details("<html></html>")
    assert data["name"] is None
    assert data["wishlists"] is None
    assert data["rating"] is None
    assert data["video"] is None


def test_fortnite_parse_full_fragment():
    html = (
        "<div class='fn-detail-name'>Escenario</div>"
        "<div class='fn-detail-type'><span>Epic</span> Emote</div>"
        "<div class='fn-item-price'>800</div>"
        "<div class='fn-detail-desc extra'>Un baile legendario</div>"
        "<table><tr><th>Source:</th><td>Shop</td></tr>"
        "<tr><th>Introduced in:</th><td>Chapter 2</td></tr>"
        "<tr><th>Release date:</th><td>2020-01-15</td></tr></table>"
        "<span data-type='wishlist'>x<span data-n='42515'></span></span>"
        "<div data-total='100' data-sum='320'></div>"
        "<video src='https://fnggcdn.com/items/999/video.mp4'></video>"
    )
    data = parse_item_details(html)
    assert data["name"] == "Escenario"
    assert data["rarity"] == "Epic"
    assert data["type"] == "Emote"
    assert data["price"] == "800"
    assert data["source"] == "Shop"
    assert data["wishlists"] == 42515
    assert data["votes"] == 100
    assert data["rating"] == 80  # 320 / (100*4) * 100
    assert data["video"] == "https://fnggcdn.com/items/999/video.mp4"


def test_fortnite_es_dicts_cover_common_values():
    assert SOURCE_ES["Shop"] == "Tienda"
    assert RARITY_ES["Legendary"] == "Legendario"
    assert TYPE_ES["Outfit"] == "Traje"
