"""Tests for core.parsing: durations, picha, ship, formatting, hygiene."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "PyArchives"))

from core.parsing import (  # noqa: E402
    clean_search,
    fmt_added,
    fmt_num,
    format_duration,
    normalize_pokemon,
    parse_duration,
    picha_for,
    ship_bar,
    ship_key,
    ship_percent,
    truncate,
)


def test_parse_duration_valid():
    assert parse_duration("10s") == 10
    assert parse_duration("10m") == 600
    assert parse_duration("2h") == 7200
    assert parse_duration("1d") == 86400
    assert parse_duration("10") == 600  # bare number defaults to minutes
    assert parse_duration("5M") == 300  # case-insensitive


def test_parse_duration_invalid():
    assert parse_duration(None) is None
    assert parse_duration("") is None
    assert parse_duration("abc") is None
    assert parse_duration("10x") is None
    assert parse_duration("0m") is None  # must be positive
    assert parse_duration("-5m") is None
    assert parse_duration("25h") is None  # over 24h max
    assert parse_duration("2d") is None
    assert parse_duration("10m", maximum=60) is None  # respects custom max


def test_parse_duration_legacy_compat():
    # Old helper accepted only s/m/h; 'd' is new. Old cases keep working.
    assert parse_duration("30s") == 30
    assert parse_duration("2h") == 7200


def test_format_duration():
    assert format_duration(45) == "45s"
    assert format_duration(90) == "1m 30s"
    assert format_duration(3600) == "1h"
    assert format_duration(90000) == "1d 1h"


def test_picha_deterministic_same_day():
    a = picha_for(12345, day_bucket=20000)
    b = picha_for(12345, day_bucket=20000)
    assert a == b
    cm, bar, comment = a
    assert 0 <= cm <= 30
    assert bar == "8" + "=" * cm + "D"
    assert isinstance(comment, str) and comment


def test_picha_varies_by_user():
    results = {picha_for(uid, day_bucket=20000)[0] for uid in range(50)}
    assert len(results) > 1  # different users get different values


def test_ship_bar_length():
    for pct in (0, 7, 50, 100):
        bar = ship_bar(pct)
        assert bar.count("❤️") == pct // 10
        assert bar.count("❤️") + bar.count("🖤") == 10


def test_picha_comment_tiers():
    # Find seeds producing each tier by brute force over day buckets.
    tiers = set()
    for uid in range(300):
        cm, _, comment = picha_for(uid, day_bucket=20000)
        if cm >= 20:
            assert comment == "Dios mío. 😳"
            tiers.add("high")
        elif cm >= 12:
            assert comment == "Respetable."
            tiers.add("mid")
        elif cm >= 6:
            assert comment == "Normal tirando a normal."
            tiers.add("low")
        else:
            assert comment == "Hay que rezar."
            tiers.add("min")
    assert tiers == {"high", "mid", "low", "min"}


def test_ship_key_symmetric():
    assert ship_key(1, 2) == ship_key(2, 1) == "1-2"


def test_ship_percent_deterministic_and_bounded():
    assert ship_percent("1-2") == ship_percent("1-2")
    for key in ("1-2", "99-100", "5-5"):
        assert 0 <= ship_percent(key) <= 100


def test_fmt_num_spanish():
    assert fmt_num(None) == "—"
    assert fmt_num(0) == "0"
    assert fmt_num(42515) == "42.515"
    assert fmt_num(1000000) == "1.000.000"


def test_fmt_added():
    assert fmt_added(None) is None
    assert fmt_added("") is None
    assert fmt_added("not-a-date") is None
    assert fmt_added("2019-11-20T12:49:44Z") == "20/11/2019"


def test_clean_search():
    assert clean_search("  Hola   Mundo  ") == "Hola Mundo"
    assert clean_search("x" * 200, max_len=100) == "x" * 100


def test_truncate():
    assert truncate("abc", 10) == "abc"
    assert truncate("a" * 20, 10) == "a" * 10 + "..."


def test_normalize_pokemon():
    assert normalize_pokemon("Mr. Mime") == "mr-mime"
    assert normalize_pokemon("  Pikachu ") == "pikachu"
    assert normalize_pokemon("Tapu-Koko") == "tapu-koko"
