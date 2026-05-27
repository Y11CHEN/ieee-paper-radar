import argparse
import logging
import sqlite3
from datetime import datetime, timedelta

import config
from db import init_db, insert_papers, get_known_dois, get_recent_papers
from fetcher import fetch_papers_ieee, enrich_with_semantic_scholar
from analyzer import summarize_papers, analyze_trends, recommend_papers
from reporter import build_email_html, send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/run.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def _date_range(days_back: int) -> tuple[str, str]:
    end = datetime.today()
    start = end - timedelta(days=days_back)
    return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")


def _week_label() -> str:
    today = datetime.today()
    return f"{today.year}-W{today.isocalendar()[1]:02d}"


def run_init() -> None:
    logger.info("Seeding %d years of historical data — no email will be sent", config.HISTORY_YEARS)
    start_date, end_date = _date_range(config.HISTORY_YEARS * 365)
    papers = fetch_papers_ieee(start_date, end_date, config.IEEE_XPLORE_API_KEY)
    papers = enrich_with_semantic_scholar(papers)

    with sqlite3.connect(config.DB_PATH) as conn:
        init_db(conn)
        known = get_known_dois(conn)
        new = [p for p in papers if p["doi"] not in known]
        insert_papers(conn, new)
    logger.info("Init complete — stored %d papers", len(new))


def run_weekly() -> None:
    logger.info("Starting weekly report")
    start_date, end_date = _date_range(config.LOOKBACK_DAYS)

    with sqlite3.connect(config.DB_PATH) as conn:
        init_db(conn)
        known = get_known_dois(conn)
        historical = get_recent_papers(conn, years=config.HISTORY_YEARS)

        papers = fetch_papers_ieee(start_date, end_date, config.IEEE_XPLORE_API_KEY)
        papers = enrich_with_semantic_scholar(papers)
        new_papers = [p for p in papers if p["doi"] not in known]

        if new_papers:
            insert_papers(conn, new_papers)

        summarized   = summarize_papers(new_papers, config.ANTHROPIC_API_KEY)
        recommended  = recommend_papers(summarized, config.RESEARCH_PROFILE, config.ANTHROPIC_API_KEY)
        trend_text   = analyze_trends(new_papers, historical, config.ANTHROPIC_API_KEY)

        row = conn.execute("SELECT COUNT(*), MIN(fetched_at) FROM papers").fetchone()
        total = row[0]
        since_raw = row[1]
        since_date = since_raw[:10] if isinstance(since_raw, str) else "N/A"

    html = build_email_html(
        new_papers=recommended,
        trend_text=trend_text,
        db_stats={"total": total, "since": since_date},
        week_label=_week_label(),
    )
    subject = f"[SC Research Weekly] {_week_label()} | {len(new_papers)} new paper(s)"
    send_email(
        html=html,
        subject=subject,
        smtp_host=config.SMTP_HOST,
        smtp_port=config.SMTP_PORT,
        sender=config.SENDER_EMAIL,
        password=config.SENDER_PASSWORD,
        recipients=config.RECIPIENT_EMAILS,
    )
    logger.info("Report sent — %d new papers this week", len(new_papers))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SC Research Weekly paper digest")
    parser.add_argument("--init", action="store_true", help="Seed 2 years of historical data (no email)")
    args = parser.parse_args()
    if args.init:
        run_init()
    else:
        run_weekly()
