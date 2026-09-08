"""Tests for core.settings validation (no crash on bad env)."""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "PyArchives"))


def _reload_settings(monkeypatch, **env):
    for key in (
        "ADMIN_ID",
        "COMMAND_PREFIX",
        "CANAL_ANUNCIOS_ID",
        "GROQ_MODEL",
        "GROQ_MAX_TOKENS",
        "PORT",
        "ENABLE_WEB",
    ):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    import core.settings as settings

    return importlib.reload(settings)


def test_defaults(monkeypatch):
    s = _reload_settings(monkeypatch)
    assert s.COMMAND_PREFIX == "cx!"
    assert s.ADMIN_ID == 979869404110159912
    assert s.PORT == 8080
    assert s.GROQ_MAX_TOKENS == 200
    assert s.MAX_PURGE_AMOUNT == 100


def test_invalid_ints_fall_back_with_warnings(monkeypatch):
    s = _reload_settings(monkeypatch, ADMIN_ID="not-a-number", PORT="abc", GROQ_MAX_TOKENS="zzz")
    assert s.ADMIN_ID == 979869404110159912
    assert s.PORT == 8080
    assert s.GROQ_MAX_TOKENS == 200
    assert len(s.CONFIG_WARNINGS) >= 3


def test_out_of_range_clamped(monkeypatch):
    s = _reload_settings(monkeypatch, PORT="99999", GROQ_MAX_TOKENS="9999")
    assert s.PORT == 65535
    assert s.GROQ_MAX_TOKENS == 1024


def test_prefix_override(monkeypatch):
    s = _reload_settings(monkeypatch, COMMAND_PREFIX="t!")
    assert s.COMMAND_PREFIX == "t!"


def test_settings_snapshot(monkeypatch):
    s = _reload_settings(monkeypatch)
    snap = s.settings_snapshot()
    assert snap.command_prefix == s.COMMAND_PREFIX
    assert snap.admin_id == s.ADMIN_ID
