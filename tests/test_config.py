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
    assert "switched capacitor" in config.KEYWORDS
    assert config.LOOKBACK_DAYS == 7
    assert config.HISTORY_YEARS == 2
