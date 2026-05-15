# SC Research Weekly — Design Spec

**Date:** 2026-05-15
**Topic:** Automated weekly paper monitoring for switched-capacitor power converters in data center applications
**Status:** Approved

---

## Overview

A local Python tool that runs weekly, fetches new research papers on switched-capacitor power converters for data centers from IEEE Xplore and Semantic Scholar, uses Claude API to summarize contributions and predict research trends, and delivers a formatted HTML email report.

---

## Architecture

```
academic trend/
├── main.py          # Entry point; orchestrates the full pipeline
├── fetcher.py       # Queries IEEE Xplore API + Semantic Scholar API
├── analyzer.py      # Calls Claude API for per-paper summaries and trend analysis
├── reporter.py      # Formats HTML email and sends via SMTP
├── db.py            # SQLite store for deduplication and historical paper data
├── config.py        # API keys, SMTP credentials, search parameters
└── logs/
    └── error.log    # Runtime errors (API failures, SMTP issues)
```

**Data flow:**
1. `fetcher` pulls papers published in the past 7 days from IEEE Xplore + Semantic Scholar
2. `db` filters out already-seen papers (keyed by DOI)
3. `analyzer` sends new papers to Claude API → per-paper contribution summaries
4. `analyzer` sends new + historical paper metadata to Claude API → trend analysis
5. `reporter` assembles HTML email and sends via SMTP
6. New papers written to SQLite for future trend context

---

## Paper Fetching

### IEEE Xplore API (primary source)
- **Keywords:** `"switched capacitor" AND ("data center" OR "server" OR "48V" OR "rack power")`
- **Venue filter:** TPEL, TIE, ECCE, APEC
- **Window:** papers published in the past 7 days (weekly run)
- **Initial seed run:** pulls 2 years of historical data on first `--init` invocation

### Semantic Scholar API (supplementary)
- For each paper found via IEEE Xplore, query by DOI or title to retrieve:
  - Citation count (used for importance ranking)
  - Reference list (used to build inter-paper context for trend analysis)

### Deduplication
- DOI is the unique key stored in SQLite
- Only papers absent from the database are passed to the analyzer

### Keywords
Defined in `config.py`; easy to extend without touching other modules.

---

## Claude API Analysis

Two separate API calls per weekly run:

### Call 1 — Per-paper summaries
**Input:** batch of new papers (title + abstract)
**Output per paper:**
- Original title
- Core contribution (2–3 sentences in English: what was done, what gap it fills, what improvement it demonstrates)
- Importance marker (⭐ or ⭐⭐) based on venue tier and citation count

### Call 2 — Trend analysis
**Input:** this week's new papers + condensed metadata (title, keywords, year) of all papers in the 2-year historical database
**Output:**
- Technology evolution narrative: a brief timeline tracing how the field has progressed, citing specific papers
- 2–3 concrete next research directions, each supported by references to existing work

---

## Email Report

**Format:** HTML email (plain-text fallback included)
**Subject line:** `[SC Research Weekly] 2026-W20 | N new papers`
**Recipients:** configurable list in `config.py` (supports multiple addresses)

**Structure:**
```
1. New This Week (N papers)
   [Title] — [Venue] [⭐⭐]
   Contribution: ...

2. Trend Analysis
   Evolution narrative: ...
   Direction 1: ... (supported by: Paper X, Paper Y)
   Direction 2: ...
   Direction 3: ...

3. Database stats
   Total papers tracked: XXX | Coverage: TPEL, TIE, ECCE, APEC | Since: YYYY-MM-DD
```

---

## Configuration (`config.py`)

```python
# API Keys
ANTHROPIC_API_KEY = "sk-ant-..."
IEEE_XPLORE_API_KEY = "..."

# Email (SMTP)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your@gmail.com"
SENDER_PASSWORD = "..."        # Gmail App Password recommended
RECIPIENT_EMAILS = ["you@gmail.com"]  # Add labmates here

# Search parameters
KEYWORDS = ["switched capacitor", "data center", "48V bus", "rack power"]
VENUES = ["TPEL", "TIE", "ECCE", "APEC"]
LOOKBACK_DAYS = 7
HISTORY_YEARS = 2
```

---

## Initialization & Scheduling

### First-time setup
```bash
python main.py --init   # Seed 2 years of historical data; no email sent
python main.py          # Manual test run; sends email
```

### Weekly automation (Windows Task Scheduler)
- Trigger: every Monday at 08:00
- Action: `python main.py` from the project directory
- Log: stdout/stderr redirected to `logs/run.log`

---

## Error Handling

- Any API call failure (IEEE Xplore, Semantic Scholar, Claude, SMTP) is caught, logged to `logs/error.log`, and does not crash the process
- If the IEEE Xplore fetch fails entirely, the email is still sent with a note: *"Paper fetch incomplete this week — see error log for details."*
- If Claude API fails, the email includes raw titles only, without AI-generated summaries
- SMTP failures are logged; no retry (user can re-run manually)

---

## Out of Scope

- Web UI or dashboard
- Real-time alerts
- Full-text PDF parsing
- Support for non-IEEE venues (e.g., Nature, arXiv) in this version
