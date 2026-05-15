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
