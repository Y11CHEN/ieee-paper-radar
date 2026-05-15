# SC Research Weekly — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a weekly automated pipeline that fetches new switched-capacitor/data-center research papers from IEEE Xplore and Semantic Scholar, summarizes them with Claude API, and emails an HTML report with trend analysis.

**Architecture:** Five focused modules (db, config, fetcher, analyzer, reporter) wired together by main.py. External API calls are isolated in fetcher.py and analyzer.py, making them easy to mock in tests. Local SQLite stores all seen papers for deduplication and historical trend context. A Windows batch file triggers the script weekly via Task Scheduler.

**Tech Stack:** Python 3.10+, `anthropic` SDK, `requests`, `sqlite3` (stdlib), `smtplib` (stdlib), `python-dotenv`, `pytest`, `pytest-mock`

---

### Task 1: Scaffold the project

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `logs/.gitkeep`
- Create: `tests/__init__.py`

- [ ] **Step 1: Initialize git repo**

```bash
cd "C:/Claude_code/Projects/Automation/academic trend"
git init
```

Expected: `Initialized empty Git repository in .../academic trend/.git/`

- [ ] **Step 2: Create requirements.txt**

```
anthropic>=0.49.0
requests>=2.31.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-mock>=3.12.0
```

- [ ] **Step 3: Create .env.example**

```
ANTHROPIC_API_KEY=sk-ant-...
IEEE_XPLORE_API_KEY=...
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAILS=you@gmail.com,labmate@gmail.com
```

- [ ] **Step 4: Create .gitignore**

```
.env
*.db
logs/*.log
logs/scheduler.log
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 5: Create logs/.gitkeep and tests/__init__.py**

```bash
mkdir -p logs tests
touch logs/.gitkeep tests/__init__.py
```

- [ ] **Step 6: Copy .env.example to .env**

```bash
cp .env.example .env
```

Then open `.env` and fill in your actual credentials. Do NOT commit this file.

- [ ] **Step 7: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: All packages install without error.

- [ ] **Step 8: Commit**

```bash
git add requirements.txt .env.example .gitignore logs/.gitkeep tests/__init__.py
git commit -m "feat: scaffold sc-research-weekly project"
```

---

### Task 2: Database module

**Files:**
- Create: `db.py`
- Create: `tests/test_db.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_db.py`:

```python
import sqlite3
import pytest
from db import init_db, insert_papers, get_known_dois, get_recent_papers


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    init_db(c)
    yield c
    c.close()


def test_init_creates_table(conn):
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='papers'")
    assert cursor.fetchone() is not None


def test_insert_and_get_known_dois(conn):
    papers = [
        {"doi": "10.1109/TPEL.2024.001", "title": "Paper A", "abstract": "...", "venue": "TPEL", "year": 2024, "citation_count": 3},
        {"doi": "10.1109/TPEL.2024.002", "title": "Paper B", "abstract": "...", "venue": "TPEL", "year": 2024, "citation_count": 0},
    ]
    insert_papers(conn, papers)
    dois = get_known_dois(conn)
    assert "10.1109/TPEL.2024.001" in dois
    assert "10.1109/TPEL.2024.002" in dois


def test_insert_ignores_duplicates(conn):
    paper = {"doi": "10.1109/TPEL.2024.001", "title": "Paper A", "abstract": "...", "venue": "TPEL", "year": 2024, "citation_count": 0}
    insert_papers(conn, [paper])
    insert_papers(conn, [paper])
    dois = get_known_dois(conn)
    assert len([d for d in dois if d == "10.1109/TPEL.2024.001"]) == 1


def test_get_recent_papers(conn):
    papers = [
        {"doi": "10.1109/TPEL.2024.001", "title": "Recent Paper", "abstract": "SC for DC", "venue": "TPEL", "year": 2024, "citation_count": 3},
        {"doi": "10.1109/TPEL.2020.001", "title": "Old Paper", "abstract": "Old work", "venue": "TPEL", "year": 2020, "citation_count": 50},
    ]
    insert_papers(conn, papers)
    recent = get_recent_papers(conn, years=2)
    dois = [p["doi"] for p in recent]
    assert "10.1109/TPEL.2024.001" in dois
    assert "10.1109/TPEL.2020.001" not in dois
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_db.py -v
```

Expected: `ModuleNotFoundError: No module named 'db'`

- [ ] **Step 3: Implement db.py**

```python
import sqlite3
from datetime import datetime


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            doi TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            abstract TEXT,
            venue TEXT,
            year INTEGER,
            citation_count INTEGER DEFAULT 0,
            fetched_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()


def insert_papers(conn: sqlite3.Connection, papers: list[dict]) -> None:
    conn.executemany(
        """INSERT OR IGNORE INTO papers (doi, title, abstract, venue, year, citation_count)
           VALUES (:doi, :title, :abstract, :venue, :year, :citation_count)""",
        papers,
    )
    conn.commit()


def get_known_dois(conn: sqlite3.Connection) -> set[str]:
    cursor = conn.execute("SELECT doi FROM papers")
    return {row[0] for row in cursor.fetchall()}


def get_recent_papers(conn: sqlite3.Connection, years: int = 2) -> list[dict]:
    cutoff_year = datetime.now().year - years
    cursor = conn.execute(
        "SELECT doi, title, abstract, venue, year, citation_count FROM papers WHERE year >= ?",
        (cutoff_year,),
    )
    cols = ["doi", "title", "abstract", "venue", "year", "citation_count"]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_db.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add db.py tests/test_db.py
git commit -m "feat: add SQLite database module with deduplication"
```

---

### Task 3: Config module

**Files:**
- Create: `config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_config.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_config.py -v
```

Expected: `ModuleNotFoundError: No module named 'config'`

- [ ] **Step 3: Implement config.py**

```python
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
IEEE_XPLORE_API_KEY: str = os.environ["IEEE_XPLORE_API_KEY"]

SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL: str = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD: str = os.environ["SENDER_PASSWORD"]
RECIPIENT_EMAILS: list[str] = os.environ["RECIPIENT_EMAILS"].split(",")

# Search parameters — edit KEYWORDS here to change what papers are tracked
KEYWORDS: list[str] = ["switched capacitor", "data center", "48V bus", "rack power"]
VENUES: dict[str, str] = {
    "TPEL": "IEEE Transactions on Power Electronics",
    "TIE": "IEEE Transactions on Industrial Electronics",
    "ECCE": "Energy Conversion Congress",
    "APEC": "Applied Power Electronics Conference",
}
LOOKBACK_DAYS: int = int(os.getenv("LOOKBACK_DAYS", "7"))
HISTORY_YEARS: int = int(os.getenv("HISTORY_YEARS", "2"))
DB_PATH: str = os.getenv("DB_PATH", "papers.db")
IEEE_API_BASE: str = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_config.py -v
```

Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add config.py tests/test_config.py
git commit -m "feat: add config module with dotenv loading"
```

---

### Task 4: IEEE Xplore fetcher

**Files:**
- Create: `fetcher.py`
- Create: `tests/test_fetcher.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_fetcher.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
from fetcher import fetch_papers_ieee

MOCK_IEEE_RESPONSE = {
    "total_records": 2,
    "articles": [
        {
            "doi": "10.1109/TPEL.2024.001",
            "title": "Switched-Capacitor Converter for 48V Data Center",
            "abstract": "This paper proposes a 2-phase SC converter...",
            "publication_title": "IEEE Transactions on Power Electronics",
            "publication_year": 2024,
        },
        {
            "doi": "10.1109/TIE.2024.002",
            "title": "Resonant SC Topology for Server Rack",
            "abstract": "We present a resonant SC converter...",
            "publication_title": "IEEE Transactions on Industrial Electronics",
            "publication_year": 2024,
        },
    ],
}


@patch("fetcher.requests.get")
def test_fetch_papers_ieee_returns_papers(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_IEEE_RESPONSE
    mock_get.return_value = mock_resp

    papers = fetch_papers_ieee(start_date="20240101", end_date="20240108", api_key="test-key")
    assert len(papers) == 2
    assert papers[0]["doi"] == "10.1109/TPEL.2024.001"
    assert papers[0]["venue"] == "TPEL"
    assert papers[1]["venue"] == "TIE"


@patch("fetcher.requests.get")
def test_fetch_papers_ieee_handles_empty(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"total_records": 0, "articles": []}
    mock_get.return_value = mock_resp

    papers = fetch_papers_ieee(start_date="20240101", end_date="20240108", api_key="test-key")
    assert papers == []


@patch("fetcher.requests.get")
def test_fetch_papers_ieee_handles_api_error(mock_get):
    mock_get.side_effect = Exception("Connection timeout")
    papers = fetch_papers_ieee(start_date="20240101", end_date="20240108", api_key="test-key")
    assert papers == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_fetcher.py -v
```

Expected: `ModuleNotFoundError: No module named 'fetcher'`

- [ ] **Step 3: Implement fetch_papers_ieee in fetcher.py**

```python
import logging
import time
import requests
from config import IEEE_API_BASE, VENUES

logger = logging.getLogger(__name__)

_VENUE_LOOKUP: dict[str, str] = {full.lower(): abbrev for abbrev, full in VENUES.items()}


def _match_venue(publication_title: str) -> str:
    title_lower = publication_title.lower()
    for fragment, abbrev in _VENUE_LOOKUP.items():
        if fragment[:20].lower() in title_lower:
            return abbrev
    return publication_title[:10]


def fetch_papers_ieee(start_date: str, end_date: str, api_key: str) -> list[dict]:
    """Fetch papers from IEEE Xplore for all configured venues."""
    all_papers: list[dict] = []
    query = "switched capacitor AND (data center OR server OR rack OR 48V)"

    for abbrev, pub_title in VENUES.items():
        start_record = 1
        while True:
            try:
                params = {
                    "apikey": api_key,
                    "querytext": query,
                    "publication_title": pub_title,
                    "start_date": start_date,
                    "end_date": end_date,
                    "start_record": start_record,
                    "max_records": 200,
                    "sort_field": "article_number",
                    "sort_order": "desc",
                }
                resp = requests.get(IEEE_API_BASE, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                articles = data.get("articles", [])
                for a in articles:
                    doi = a.get("doi", "").strip()
                    if not doi:
                        continue
                    all_papers.append({
                        "doi": doi,
                        "title": a.get("title", ""),
                        "abstract": a.get("abstract", ""),
                        "venue": abbrev,
                        "year": int(a.get("publication_year", 0)),
                        "citation_count": 0,
                    })
                total = int(data.get("total_records", 0))
                if start_record + len(articles) - 1 >= total or not articles:
                    break
                start_record += len(articles)
            except Exception as e:
                logger.error("IEEE Xplore fetch failed for %s: %s", abbrev, e)
                break

    return all_papers
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_fetcher.py -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add fetcher.py tests/test_fetcher.py
git commit -m "feat: add IEEE Xplore fetcher with pagination and per-venue search"
```

---

### Task 5: Semantic Scholar enricher

**Files:**
- Modify: `fetcher.py` (add `enrich_with_semantic_scholar`)
- Modify: `tests/test_fetcher.py` (add enrichment tests)

- [ ] **Step 1: Write failing tests**

Append to `tests/test_fetcher.py`:

```python
from fetcher import enrich_with_semantic_scholar


@patch("fetcher.requests.get")
def test_enrich_adds_citation_count(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"citationCount": 12}
    mock_get.return_value = mock_resp

    papers = [{"doi": "10.1109/TPEL.2024.001", "title": "SC Converter", "citation_count": 0}]
    enriched = enrich_with_semantic_scholar(papers)
    assert enriched[0]["citation_count"] == 12


@patch("fetcher.requests.get")
def test_enrich_handles_not_found(mock_get):
    not_found = MagicMock()
    not_found.status_code = 404
    fallback = MagicMock()
    fallback.status_code = 200
    fallback.json.return_value = {"data": []}
    mock_get.side_effect = [not_found, fallback]

    papers = [{"doi": "10.1109/TPEL.2024.999", "title": "Unknown Paper", "citation_count": 0}]
    enriched = enrich_with_semantic_scholar(papers)
    assert enriched[0]["citation_count"] == 0
```

- [ ] **Step 2: Run new tests to verify they fail**

```bash
pytest tests/test_fetcher.py::test_enrich_adds_citation_count tests/test_fetcher.py::test_enrich_handles_not_found -v
```

Expected: `ImportError: cannot import name 'enrich_with_semantic_scholar'`

- [ ] **Step 3: Add enrich_with_semantic_scholar to fetcher.py**

Append to `fetcher.py`:

```python
_SS_BASE = "https://api.semanticscholar.org/graph/v1/paper"


def enrich_with_semantic_scholar(papers: list[dict]) -> list[dict]:
    """Adds citation_count to each paper by querying Semantic Scholar. Mutates in place."""
    for paper in papers:
        doi = paper.get("doi", "")
        if not doi:
            continue
        try:
            resp = requests.get(f"{_SS_BASE}/DOI:{doi}", params={"fields": "citationCount"}, timeout=15)
            if resp.status_code == 200:
                paper["citation_count"] = resp.json().get("citationCount", 0)
            elif resp.status_code == 404:
                resp2 = requests.get(
                    f"{_SS_BASE}/search",
                    params={"query": paper["title"], "fields": "citationCount", "limit": 1},
                    timeout=15,
                )
                if resp2.status_code == 200:
                    data = resp2.json().get("data", [])
                    if data:
                        paper["citation_count"] = data[0].get("citationCount", 0)
            time.sleep(0.1)
        except Exception as e:
            logger.warning("Semantic Scholar lookup failed for %s: %s", doi, e)
    return papers
```

- [ ] **Step 4: Run all fetcher tests**

```bash
pytest tests/test_fetcher.py -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add fetcher.py tests/test_fetcher.py
git commit -m "feat: add Semantic Scholar enrichment for citation counts"
```

---

### Task 6: Claude API paper summarizer

**Files:**
- Create: `analyzer.py`
- Create: `tests/test_analyzer.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_analyzer.py`:

```python
import pytest
from unittest.mock import MagicMock, patch
from analyzer import summarize_papers

SAMPLE_PAPERS = [
    {
        "doi": "10.1109/TPEL.2024.001",
        "title": "High-Efficiency Switched-Capacitor Converter for 48V Data Center",
        "abstract": "This paper presents a novel 2-phase SC converter achieving 98.5% efficiency...",
        "venue": "TPEL",
        "year": 2024,
        "citation_count": 5,
    }
]


@patch("analyzer.anthropic.Anthropic")
def test_summarize_papers_returns_summaries(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text='[{"doi": "10.1109/TPEL.2024.001", "contribution": "Proposes a 2-phase SC converter with 98.5% efficiency for 48V data center bus.", "stars": "⭐⭐"}]')]
    )

    result = summarize_papers(SAMPLE_PAPERS, api_key="sk-ant-test")
    assert len(result) == 1
    assert result[0]["doi"] == "10.1109/TPEL.2024.001"
    assert "contribution" in result[0]
    assert result[0]["stars"] in ("⭐", "⭐⭐")


@patch("analyzer.anthropic.Anthropic")
def test_summarize_papers_empty_input(mock_cls):
    result = summarize_papers([], api_key="sk-ant-test")
    assert result == []
    mock_cls.return_value.messages.create.assert_not_called()


@patch("analyzer.anthropic.Anthropic")
def test_summarize_papers_falls_back_on_api_error(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.side_effect = Exception("API error")

    result = summarize_papers(SAMPLE_PAPERS, api_key="sk-ant-test")
    assert len(result) == 1
    assert result[0]["contribution"] == "Summary unavailable."
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_analyzer.py -v
```

Expected: `ModuleNotFoundError: No module named 'analyzer'`

- [ ] **Step 3: Implement summarize_papers in analyzer.py**

```python
import json
import logging
import anthropic

logger = logging.getLogger(__name__)

_SUMMARIZE_PROMPT = """\
You are a power electronics research assistant. Summarize each paper below.

Return a JSON array only — no markdown, no prose, no code fences. One object per paper:
{{"doi": "<doi>", "contribution": "<2-3 sentences: what was done, what gap it fills, key result>", "stars": "<⭐⭐ for TPEL/TIE, ⭐ for ECCE/APEC>"}}

Papers:
{papers_text}
"""


def summarize_papers(papers: list[dict], api_key: str) -> list[dict]:
    if not papers:
        return []

    papers_text = "\n\n".join(
        f"DOI: {p['doi']}\nTitle: {p['title']}\nVenue: {p['venue']}\nAbstract: {p['abstract']}"
        for p in papers
    )

    client = anthropic.Anthropic(api_key=api_key)
    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": _SUMMARIZE_PROMPT.format(papers_text=papers_text)}],
        )
        summaries = json.loads(msg.content[0].text.strip())
    except Exception as e:
        logger.error("Claude summarize failed: %s", e)
        return [
            {**p, "contribution": "Summary unavailable.", "stars": "⭐" if p["venue"] in ("ECCE", "APEC") else "⭐⭐"}
            for p in papers
        ]

    doi_map = {s["doi"]: s for s in summaries}
    return [
        {
            **p,
            "contribution": doi_map.get(p["doi"], {}).get("contribution", "Summary unavailable."),
            "stars": doi_map.get(p["doi"], {}).get("stars", "⭐⭐" if p["venue"] in ("TPEL", "TIE") else "⭐"),
        }
        for p in papers
    ]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_analyzer.py -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add analyzer.py tests/test_analyzer.py
git commit -m "feat: add Claude API paper summarizer with fallback"
```

---

### Task 7: Claude API trend analyzer

**Files:**
- Modify: `analyzer.py` (add `analyze_trends`)
- Modify: `tests/test_analyzer.py` (add trend tests)

- [ ] **Step 1: Write failing tests**

Append to `tests/test_analyzer.py`:

```python
from analyzer import analyze_trends

HISTORICAL_PAPERS = [
    {"title": "SC Converter 48V Bus 2023", "venue": "TPEL", "year": 2023},
    {"title": "Resonant SC for Rack 2022", "venue": "ECCE", "year": 2022},
]


@patch("analyzer.anthropic.Anthropic")
def test_analyze_trends_returns_text(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="**Evolution:** SC converters have moved from...\n\n**Direction 1:** Soft charging...")]
    )

    result = analyze_trends(SAMPLE_PAPERS, HISTORICAL_PAPERS, api_key="sk-ant-test")
    assert isinstance(result, str)
    assert len(result) > 20


@patch("analyzer.anthropic.Anthropic")
def test_analyze_trends_handles_api_error(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.side_effect = Exception("API error")

    result = analyze_trends(SAMPLE_PAPERS, HISTORICAL_PAPERS, api_key="sk-ant-test")
    assert "unavailable" in result.lower()
```

- [ ] **Step 2: Run new tests to verify they fail**

```bash
pytest tests/test_analyzer.py::test_analyze_trends_returns_text tests/test_analyzer.py::test_analyze_trends_handles_api_error -v
```

Expected: `ImportError: cannot import name 'analyze_trends'`

- [ ] **Step 3: Add analyze_trends to analyzer.py**

Append to `analyzer.py`:

```python
_TREND_PROMPT = """\
You are an expert in switched-capacitor power converters for data center applications.

New papers this week:
{new_papers_text}

Historical context ({hist_count} papers from the past 2 years):
{hist_papers_text}

Write a concise research trend analysis in English with exactly these sections:

**Evolution Narrative** (3-5 sentences): How has this field progressed? Cite specific paper titles.

**Direction 1**: The most likely next research direction. Cite supporting evidence from existing work.

**Direction 2**: A second promising direction with evidence.

**Direction 3**: A third direction worth watching.

Be specific. Reference actual paper titles when making claims.
"""


def analyze_trends(new_papers: list[dict], historical_papers: list[dict], api_key: str) -> str:
    new_text = "\n".join(f"- {p['title']} ({p['venue']}, {p['year']})" for p in new_papers) or "(none this week)"
    hist_text = "\n".join(
        f"- {p['title']} ({p['venue']}, {p['year']})"
        for p in sorted(historical_papers, key=lambda x: x["year"], reverse=True)[:80]
    )

    client = anthropic.Anthropic(api_key=api_key)
    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": _TREND_PROMPT.format(
                    new_papers_text=new_text,
                    hist_count=len(historical_papers),
                    hist_papers_text=hist_text,
                ),
            }],
        )
        return msg.content[0].text.strip()
    except Exception as e:
        logger.error("Claude trend analysis failed: %s", e)
        return "Trend analysis unavailable this week due to an API error."
```

- [ ] **Step 4: Run all analyzer tests**

```bash
pytest tests/test_analyzer.py -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add analyzer.py tests/test_analyzer.py
git commit -m "feat: add Claude API trend analyzer with historical context"
```

---

### Task 8: Email reporter

**Files:**
- Create: `reporter.py`
- Create: `tests/test_reporter.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_reporter.py`:

```python
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
    mock_server.sendmail.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_reporter.py -v
```

Expected: `ModuleNotFoundError: No module named 'reporter'`

- [ ] **Step 3: Implement reporter.py**

```python
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def build_email_html(
    new_papers: list[dict],
    trend_text: str,
    db_stats: dict,
    week_label: str,
) -> str:
    if new_papers:
        paper_rows = "".join(
            f"""<div style="margin-bottom:20px;padding:12px;border-left:3px solid #0057a8;">
              <p style="margin:0 0 4px 0;font-size:15px;font-weight:bold;">{p['stars']} {p['title']}</p>
              <p style="margin:0 0 4px 0;color:#666;font-size:12px;">
                {p['venue']} &middot; {p['year']} &middot; Citations: {p['citation_count']} &middot;
                <a href="https://doi.org/{p['doi']}">{p['doi']}</a>
              </p>
              <p style="margin:0;font-size:13px;">{p['contribution']}</p>
            </div>"""
            for p in new_papers
        )
    else:
        paper_rows = "<p>No new papers found this week.</p>"

    trend_html = trend_text.replace("\n", "<br>")

    return f"""<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;color:#222;padding:20px;">
  <h2 style="color:#0057a8;">[SC Research Weekly] {week_label}</h2>

  <h3>New Papers This Week ({len(new_papers)})</h3>
  {paper_rows}

  <hr style="border:none;border-top:1px solid #ddd;margin:24px 0;">

  <h3>Research Trend Analysis</h3>
  <p style="font-size:13px;line-height:1.8;">{trend_html}</p>

  <hr style="border:none;border-top:1px solid #ddd;margin:24px 0;">

  <p style="font-size:11px;color:#999;">
    Database: {db_stats['total']} papers tracked &middot;
    Coverage: TPEL, TIE, ECCE, APEC &middot;
    Since: {db_stats['since']}
  </p>
</body>
</html>"""


def send_email(
    html: str,
    subject: str,
    smtp_host: str,
    smtp_port: int,
    sender: str,
    password: str,
    recipients: list[str],
) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())
    logger.info("Email sent to %s", recipients)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_reporter.py -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add reporter.py tests/test_reporter.py
git commit -m "feat: add HTML email builder and SMTP sender"
```

---

### Task 9: Main entry point

**Files:**
- Create: `main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_main.py`:

```python
from unittest.mock import patch, MagicMock
from main import run_weekly, run_init


@patch("main.send_email")
@patch("main.analyze_trends", return_value="Direction 1: soft charging.")
@patch("main.summarize_papers")
@patch("main.enrich_with_semantic_scholar")
@patch("main.fetch_papers_ieee")
@patch("main.insert_papers")
@patch("main.get_recent_papers", return_value=[])
@patch("main.get_known_dois", return_value=set())
@patch("main.init_db")
@patch("main.sqlite3.connect")
def test_run_weekly_sends_email(
    mock_connect, mock_init_db, mock_known, mock_recent,
    mock_insert, mock_fetch, mock_enrich, mock_summarize, mock_trends, mock_send
):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = (10, "2024-01-01T00:00:00")
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=mock_conn)
    ctx.__exit__ = MagicMock(return_value=False)
    mock_connect.return_value = ctx

    paper = {"doi": "10.1109/TPEL.2024.001", "title": "SC Paper", "abstract": "...", "venue": "TPEL", "year": 2024, "citation_count": 0}
    mock_fetch.return_value = [paper]
    mock_enrich.return_value = [paper]
    mock_summarize.return_value = [{**paper, "contribution": "Great result.", "stars": "⭐⭐"}]

    run_weekly()
    mock_send.assert_called_once()


@patch("main.insert_papers")
@patch("main.enrich_with_semantic_scholar", return_value=[])
@patch("main.fetch_papers_ieee", return_value=[])
@patch("main.get_known_dois", return_value=set())
@patch("main.init_db")
@patch("main.sqlite3.connect")
def test_run_init_does_not_send_email(mock_connect, mock_init, mock_known, mock_fetch, mock_enrich, mock_insert):
    mock_conn = MagicMock()
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=mock_conn)
    ctx.__exit__ = MagicMock(return_value=False)
    mock_connect.return_value = ctx

    with patch("main.send_email") as mock_send:
        run_init()
        mock_send.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_main.py -v
```

Expected: `ModuleNotFoundError: No module named 'main'`

- [ ] **Step 3: Implement main.py**

```python
import argparse
import logging
import sqlite3
from datetime import datetime, timedelta

import config
from db import init_db, insert_papers, get_known_dois, get_recent_papers
from fetcher import fetch_papers_ieee, enrich_with_semantic_scholar
from analyzer import summarize_papers, analyze_trends
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

        summarized = summarize_papers(new_papers, config.ANTHROPIC_API_KEY)
        trend_text = analyze_trends(new_papers, historical, config.ANTHROPIC_API_KEY)

        row = conn.execute("SELECT COUNT(*), MIN(fetched_at) FROM papers").fetchone()
        total = row[0]
        since_raw = row[1]
        since_date = since_raw[:10] if isinstance(since_raw, str) else "N/A"

    html = build_email_html(
        new_papers=summarized,
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
```

- [ ] **Step 4: Run all tests**

```bash
pytest tests/ -v
```

Expected: All 13 tests pass.

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: add main entry point with --init and weekly pipeline"
```

---

### Task 10: Windows Task Scheduler setup

**Files:**
- Create: `run_weekly.bat`

- [ ] **Step 1: Create the batch launcher**

Create `run_weekly.bat` in the project root:

```bat
@echo off
cd /d "C:\Claude_code\Projects\Automation\academic trend"
python main.py >> logs\scheduler.log 2>&1
```

- [ ] **Step 2: Open Task Scheduler**

Press `Win + R`, type `taskschd.msc`, press Enter.

- [ ] **Step 3: Create a new task**

Click **"Create Task"** (not "Create Basic Task") in the right-hand Actions panel.

**General tab:**
- Name: `SC Research Weekly`
- Check: "Run whether user is logged on or not"
- Check: "Run with highest privileges"

**Triggers tab → New:**
- Begin the task: On a schedule → Weekly
- Recur every 1 week on: Monday
- Start time: 08:00:00
- Check: Enabled

**Actions tab → New:**
- Action: Start a program
- Program/script: `C:\Claude_code\Projects\Automation\academic trend\run_weekly.bat`
- Start in: `C:\Claude_code\Projects\Automation\academic trend`

**Settings tab:**
- Check: "Run task as soon as possible after a scheduled start is missed"
- If the task fails, restart every: 1 hour, attempt up to 3 times

Click OK and enter your Windows password when prompted.

- [ ] **Step 4: Test the task immediately**

Right-click `SC Research Weekly` in the task list → **Run**.

Wait ~30 seconds, then check `logs\scheduler.log`:

```bash
type logs\scheduler.log
```

Expected: Log shows INFO lines ending with `Report sent — N new papers this week`

- [ ] **Step 5: Commit**

```bash
git add run_weekly.bat
git commit -m "feat: add Windows Task Scheduler batch launcher"
```

---

### Task 11: First real run

- [ ] **Step 1: Verify .env credentials**

Open `.env` and confirm all fields are filled:

| Key | Where to get it |
|-----|----------------|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
| `IEEE_XPLORE_API_KEY` | developer.ieee.org → free registration → My Keys |
| `SENDER_EMAIL` | Your Gmail address |
| `SENDER_PASSWORD` | Gmail → My Account → Security → 2-Step Verification → App Passwords → Generate one for "Mail" |
| `RECIPIENT_EMAILS` | Comma-separated list of addresses to receive the digest |

- [ ] **Step 2: Seed historical data**

```bash
python main.py --init
```

Expected output (takes 1-3 minutes):
```
INFO main: Seeding 2 years of historical data — no email will be sent
INFO main: Init complete — stored N papers
```

- [ ] **Step 3: Send first weekly report manually**

```bash
python main.py
```

Expected: Email arrives in inbox within ~60 seconds.

- [ ] **Step 4: Confirm all tests still pass**

```bash
pytest tests/ -v
```

Expected: All 13 tests pass.
