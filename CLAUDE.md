# CLAUDE.md — academic trend

A weekly automated pipeline that fetches power-electronics papers from IEEE Xplore, enriches them with Semantic Scholar citation counts, summarizes them with Claude, and emails an HTML digest.

## Setup

```bash
# Python version is pinned in .python-version
pip install -r requirements.txt
cp .env.example .env   # then fill in real keys
```

Required `.env` keys: `ANTHROPIC_API_KEY`, `IEEE_XPLORE_API_KEY`, `SENDER_EMAIL`, `SENDER_PASSWORD`, `RECIPIENT_EMAILS`.  
Optional overrides: `SMTP_HOST`, `SMTP_PORT`, `LOOKBACK_DAYS`, `HISTORY_YEARS`, `DB_PATH`.

## Run

```bash
# First-time only: seed 2 years of historical papers (no email sent)
python main.py --init

# Weekly digest (fetch → enrich → summarize → analyze → email)
python main.py
```

Windows Task Scheduler calls `run_weekly.bat`, which wraps `python main.py` and appends to `logs\scheduler.log`.

## Tests

```bash
python -m pytest tests/ -v            # all tests
python -m pytest tests/test_db.py -v  # single module
```

Tests use `pytest-mock` to stub the Claude API, IEEE Xplore, and Semantic Scholar calls. No real API calls are made during tests.

## Architecture

Data flows left-to-right through four stages, each in its own module:

```
fetcher.py  →  db.py  →  analyzer.py  →  reporter.py
```

| Module | Role |
|---|---|
| `config.py` | Loads all env vars and constants (keywords, venues, paths) |
| `fetcher.py` | `fetch_papers_ieee()` paginates IEEE Xplore; `enrich_with_semantic_scholar()` adds citation counts |
| `db.py` | SQLite helpers — `init_db`, `insert_papers`, `get_known_dois`, `get_recent_papers` |
| `analyzer.py` | `summarize_papers()` calls Claude for per-paper summaries; `analyze_trends()` calls Claude for the trend narrative |
| `reporter.py` | `build_email_html()` renders the digest; `send_email()` sends via SMTP |
| `main.py` | Orchestrates `run_init()` and `run_weekly()` flows |

**DOI is the primary key** — `get_known_dois()` is used before every insert to skip already-stored papers.

**Venue abbreviations** (`TPEL`, `TIE`, `ECCE`, `APEC`) are defined in `config.VENUES` and control both the IEEE query and the ⭐/⭐⭐ star rating in summaries.

To change tracked keywords or add a new venue, edit `config.py` only — no other file needs to change.

## Claude API usage

All three functions (`summarize_papers`, `analyze_trends`, `recommend_papers`) use `gemini-2.5-pro`. The model name is hardcoded in `analyzer.py`; update all three calls together if upgrading.
