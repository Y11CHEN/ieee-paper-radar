import pytest


def test_config_loads_required_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test")
    monkeypatch.setenv("IEEE_XPLORE_API_KEY", "ieee-test")
    monkeypatch.setenv("SENDER_EMAIL", "test@gmail.com")
    monkeypatch.setenv("SENDER_PASSWORD", "pass")
    import importlib, config
    importlib.reload(config)
    assert config.GEMINI_API_KEY == "gemini-test"
    assert isinstance(config.RECIPIENT_EMAILS, list)
    assert len(config.RECIPIENT_EMAILS) > 0


def test_config_has_default_keywords():
    import config
    assert "switched capacitor" in config.KEYWORDS_REQUIRED
    assert "data center" in config.KEYWORDS_CONTEXT
    assert "server rack" in config.KEYWORDS_CONTEXT
    assert config.LOOKBACK_DAYS == 14
    assert config.HISTORY_YEARS == 2


def test_config_has_research_profile():
    import config
    assert "switched capacitor" in config.RESEARCH_PROFILE.lower()
    assert len(config.RESEARCH_PROFILE) > 50


def test_config_has_full_venue_names():
    import config
    assert "Exposition" in config.VENUES["ECCE"]
    assert "Exposition" in config.VENUES["APEC"]
