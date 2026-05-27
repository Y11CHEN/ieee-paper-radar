import pytest


def test_config_loads_required_keys(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("IEEE_XPLORE_API_KEY", "ieee-test")
    monkeypatch.setenv("SENDER_EMAIL", "test@gmail.com")
    monkeypatch.setenv("SENDER_PASSWORD", "pass")
    monkeypatch.setenv("RECIPIENT_EMAILS", "a@b.com,c@d.com")
    import importlib, config
    importlib.reload(config)
    assert config.ANTHROPIC_API_KEY == "sk-ant-test"
    assert config.RECIPIENT_EMAILS == ["a@b.com", "c@d.com"]


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
