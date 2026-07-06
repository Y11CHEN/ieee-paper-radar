from unittest.mock import patch, MagicMock
from reporter import build_email_html, send_email

SAMPLE_PAPERS = [
    {
        "doi": "10.1109/TPEL.2024.001",
        "title": "High-Efficiency SC Converter for 48V Data Center",
        "venue": "TPEL",
        "year": 2024,
        "citation_count": 5,
        "contribution": "Proposes a 2-phase SC converter achieving 98.5% efficiency.",
        "stars": "⭐⭐",
    }
]


def test_build_email_html_contains_key_fields():
    html = build_email_html(
        new_papers=SAMPLE_PAPERS,
        trend_text="Direction 1: Soft charging techniques...",
        db_stats={"total": 42, "since": "2024-01-01"},
        week_label="2026-W20",
    )
    assert "High-Efficiency SC Converter" in html
    assert "Direction 1" in html
    assert "42" in html
    assert "⭐⭐" in html
    assert "10.1109/TPEL.2024.001" in html


def test_build_email_html_no_papers():
    html = build_email_html(
        new_papers=[],
        trend_text="No new papers this week.",
        db_stats={"total": 10, "since": "2024-01-01"},
        week_label="2026-W20",
    )
    assert "No new papers" in html


def test_build_email_html_shows_error_banner():
    html = build_email_html(
        new_papers=[],
        trend_text="Trend analysis unavailable this week due to an API error.",
        db_stats={"total": 10, "since": "2024-01-01"},
        week_label="2026-W20",
        errors=["IEEE Xplore fetch failed for TPEL: 403 Forbidden"],
    )
    assert "步骤失败" in html
    assert "IEEE Xplore fetch failed for TPEL: 403 Forbidden" in html


def test_build_email_html_no_banner_when_no_errors():
    html = build_email_html(
        new_papers=[],
        trend_text="All good.",
        db_stats={"total": 10, "since": "2024-01-01"},
        week_label="2026-W20",
    )
    assert "步骤失败" not in html


@patch("reporter.smtplib.SMTP")
def test_send_email_calls_smtp(mock_smtp_class):
    mock_server = MagicMock()
    mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

    send_email(
        html="<html>test</html>",
        subject="Test Subject",
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        sender="a@b.com",
        password="pass",
        recipients=["c@d.com"],
    )
    mock_server.ehlo.assert_called_once()
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("a@b.com", "pass")
    mock_server.sendmail.assert_called_once()


def test_build_email_html_shows_recommendation_section():
    papers_with_tier = [
        {
            "doi": "10.1109/TPEL.2024.001",
            "title": "High-Efficiency SC Converter for 48V Data Center",
            "venue": "TPEL",
            "year": 2024,
            "citation_count": 5,
            "contribution": "Proposes a 2-phase SC converter achieving 98.5% efficiency.",
            "stars": "⭐⭐",
            "tier": "强烈推荐",
            "reason": "直接推进 RSCC 拓扑推导方法",
        }
    ]
    html = build_email_html(
        new_papers=papers_with_tier,
        trend_text="Direction 1: Soft charging techniques...",
        db_stats={"total": 42, "since": "2024-01-01"},
        week_label="2026-W20",
    )
    assert "本周推荐" in html
    assert "强烈推荐" in html
    assert "直接推进 RSCC 拓扑推导方法" in html


def test_build_email_html_shows_both_tiers():
    papers = [
        {
            "doi": "10.1109/TPEL.2024.001",
            "title": "Paper A",
            "venue": "TPEL",
            "year": 2024,
            "citation_count": 5,
            "contribution": "...",
            "stars": "⭐⭐",
            "tier": "强烈推荐",
            "reason": "非常相关",
        },
        {
            "doi": "10.1109/ECCE.2024.002",
            "title": "Paper B",
            "venue": "ECCE",
            "year": 2024,
            "citation_count": 1,
            "contribution": "...",
            "stars": "⭐",
            "tier": "值得一读",
            "reason": "可以参考",
        },
    ]
    html = build_email_html(
        new_papers=papers,
        trend_text="...",
        db_stats={"total": 10, "since": "2024-01-01"},
        week_label="2026-W20",
    )
    assert "强烈推荐" in html
    assert "值得一读" in html
    assert "非常相关" in html
    assert "可以参考" in html


def test_build_email_html_no_rec_section_when_all_skipped():
    papers_skipped = [
        {
            "doi": "10.1109/TPEL.2024.001",
            "title": "High-Efficiency SC Converter",
            "venue": "TPEL",
            "year": 2024,
            "citation_count": 5,
            "contribution": "...",
            "stars": "⭐⭐",
            "tier": "跳过",
            "reason": "不相关",
        }
    ]
    html = build_email_html(
        new_papers=papers_skipped,
        trend_text="...",
        db_stats={"total": 10, "since": "2024-01-01"},
        week_label="2026-W20",
    )
    assert "本周推荐" not in html


def test_build_email_html_no_rec_section_without_tier_field():
    html = build_email_html(
        new_papers=SAMPLE_PAPERS,
        trend_text="Direction 1: ...",
        db_stats={"total": 42, "since": "2024-01-01"},
        week_label="2026-W20",
    )
    assert "本周推荐" not in html
    assert "High-Efficiency SC Converter" in html
