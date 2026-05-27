# IEEE Paper Radar

A weekly automation pipeline that monitors IEEE Xplore for new papers, ranks them by personal relevance using AI, and delivers a curated digest to your inbox every week.

[中文](README_zh.md) | [한국어](README_ko.md)

## What It Does

1. **Fetches** new papers from IEEE Xplore across configured venues (TPEL, TIE, ECCE, APEC)
2. **Enriches** each paper with citation counts from Semantic Scholar
3. **Summarizes** each paper's contribution in 2–3 sentences using Gemini AI
4. **Recommends** must-read papers ranked against your research profile (强烈推荐 / 值得一读 / 跳过)
5. **Analyzes** research trends across the past 2 years of literature
6. **Emails** a formatted HTML digest to your inbox

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your research direction

Edit the **USER SETTINGS** section at the top of `config.py`:

```python
# Who receives the weekly digest
RECIPIENT_EMAILS = ["you@gmail.com"]

# Search query: papers must match ALL required + at least one context keyword
KEYWORDS_REQUIRED = ["switched capacitor"]
KEYWORDS_CONTEXT  = ["data center", "48V bus", "rack power", "server rack"]

# IEEE venues to monitor
VENUES = {
    "TPEL": "IEEE Transactions on Power Electronics",
    ...
}

# Your research profile — the AI uses this to rank paper relevance
RESEARCH_PROFILE = """
Focus: ...
Key interests: ...
"""
```

### 3. Set up secrets

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```
GEMINI_API_KEY=AIza...          # aistudio.google.com/apikey (free)
IEEE_XPLORE_API_KEY=...         # developer.ieee.org (free)
SENDER_EMAIL=you@gmail.com
SENDER_PASSWORD=xxxx-xxxx-xxxx  # Gmail App Password, not your account password
```

> **Gmail App Password:** Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) and generate one.

## Usage

```bash
# First run only: seed 2 years of historical papers (no email sent)
python main.py --init

# Weekly digest: fetch → enrich → summarize → recommend → email
python main.py
```

### Automate with Windows Task Scheduler

`run_weekly.bat` is included for use with Windows Task Scheduler. Set it to run every Monday morning.

## Email Format

```
[IEEE Paper Radar] 2026-W22 | 5 new papers

📚 本周推荐
  ── 强烈推荐 ──────────────────────────
  ⭐⭐ A Soft-Switching Multiresonant...  (TPEL)
  理由: Directly advances RSCC topology derivation...

  ── 值得一读 ──────────────────────────
  ⭐ Flying Capacitor Multilevel...  (ECCE)

── All New Papers (5) ────────────────
  [1] ⭐⭐ Title — TPEL · 2026 · Citations: 3
      Contribution: ...

── Research Trend Analysis ───────────
  Evolution Narrative: ...
  Direction 1: ...
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Paper source | IEEE Xplore API |
| Citation counts | Semantic Scholar API |
| AI analysis | Google Gemini 2.5 Pro |
| Database | SQLite |
| Email | SMTP (Gmail) |
| Language | Python 3.12+ |

## Tests

```bash
python -m pytest tests/ -v
```

All external APIs are mocked — no real API calls during tests.
