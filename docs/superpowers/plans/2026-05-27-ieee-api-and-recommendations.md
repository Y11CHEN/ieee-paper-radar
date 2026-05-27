# IEEE API Fixes & Paper Recommendation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix three query/config bugs that silently degrade result quality, then add a `recommend_papers()` function that scores each paper on technical impact and personal relevance and renders a "本周推荐" section at the top of the weekly email.

**Architecture:** Five focused tasks touch seven files. Config changes (Task 1) cascade into fetcher (Task 2). The new analyzer function (Task 3) slots in between existing `summarize_papers` and `analyze_trends` calls. Reporter (Task 4) renders the new tier field; main (Task 5) wires everything together. All changes are TDD: failing test → implementation → passing test → commit.

**Tech Stack:** Python 3.10+, `anthropic` SDK, `sqlite3`, `smtplib`, `pytest`, `pytest-mock`

---

### Task 1: Update config.py and fix fetcher.py import

**Files:**
- Modify: `config.py`
- Modify: `fetcher.py` (import line only — query logic fixed in Task 2)
- Modify: `tests/test_config.py`

- [ ] **Step 1: Write failing config tests**

Replace the entire `tests/test_config.py` with:

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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd "C:\Claude_code\Projects\Automation\academic trend"
python -m pytest tests/test_config.py -v
```

Expected: `FAILED tests/test_config.py::test_config_has_default_keywords` — `AttributeError: module 'config' has no attribute 'KEYWORDS_REQUIRED'`

- [ ] **Step 3: Update config.py**

Replace the entire content of `config.py` with:

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
RECIPIENT_EMAILS: list[str] = [e.strip() for e in os.environ["RECIPIENT_EMAILS"].split(",")]

KEYWORDS_REQUIRED: list[str] = ["switched capacitor"]
KEYWORDS_CONTEXT: list[str] = ["data center", "48V bus", "rack power", "server rack"]

VENUES: dict[str, str] = {
    "TPEL": "IEEE Transactions on Power Electronics",
    "TIE":  "IEEE Transactions on Industrial Electronics",
    "ECCE": "IEEE Energy Conversion Congress and Exposition",
    "APEC": "IEEE Applied Power Electronics Conference and Exposition",
}

LOOKBACK_DAYS: int = int(os.getenv("LOOKBACK_DAYS", "14"))
HISTORY_YEARS: int = int(os.getenv("HISTORY_YEARS", "2"))
DB_PATH: str = os.getenv("DB_PATH", "papers.db")
IEEE_API_BASE: str = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

RESEARCH_PROFILE: str = os.getenv("RESEARCH_PROFILE", """
Focus: Resonant and soft-switching switched-capacitor converters (RSCC) for 48V data center power delivery.
Key interests:
- Soft-charging / ZCS operation in SC topologies (SSL/FSL modeling framework)
- Multi-phase resonant SC converter design and analysis
- Flying-capacitor multilevel and Dickson-based topologies
- Pilawa-Podgurski group publications
- Topology derivation and extension methods
Prioritize papers that advance circuit-level analysis or introduce new topologies over system-level/application papers.
""")
```

- [ ] **Step 4: Fix the import line in fetcher.py**

Change line 4 of `fetcher.py` from:

```python
from config import IEEE_API_BASE, VENUES, KEYWORDS
```

to:

```python
from config import IEEE_API_BASE, VENUES, KEYWORDS_REQUIRED, KEYWORDS_CONTEXT
```

(Query construction is still broken at this point — fixed in Task 2.)

- [ ] **Step 5: Run config tests to verify they pass**

```bash
python -m pytest tests/test_config.py -v
```

Expected: `4 passed`

- [ ] **Step 6: Commit**

```bash
git add config.py fetcher.py tests/test_config.py
git commit -m "feat: split KEYWORDS into required/context, fix venue names, add RESEARCH_PROFILE"
```

---

### Task 2: Fix fetcher.py query construction

**Files:**
- Modify: `fetcher.py` (query construction block only)

- [ ] **Step 1: Run existing fetcher tests to establish baseline**

```bash
python -m pytest tests/test_fetcher.py -v
```

Expected: `5 passed` (the mock tests don't inspect the query string, so they pass even with the broken import from Task 1 — but now the import is fixed)

- [ ] **Step 2: Update query construction in fetcher.py**

In `fetcher.py`, replace lines 10–13 (inside `fetch_papers_ieee`, before the `for` loop):

Old code:
```python
    all_papers: list[dict] = []
    seen_dois: set[str] = set()
    query_terms = " OR ".join(f'"{k}"' for k in KEYWORDS)
    query = f"({query_terms})"
```

New code:
```python
    all_papers: list[dict] = []
    seen_dois: set[str] = set()
    required = " AND ".join(f'"{k}"' for k in KEYWORDS_REQUIRED)
    context  = " OR ".join(f'"{k}"' for k in KEYWORDS_CONTEXT)
    query    = f"({required}) AND ({context})"
```

- [ ] **Step 3: Run fetcher tests to verify they still pass**

```bash
python -m pytest tests/test_fetcher.py -v
```

Expected: `5 passed`

- [ ] **Step 4: Commit**

```bash
git add fetcher.py
git commit -m "fix: change IEEE query from OR to AND logic to eliminate irrelevant papers"
```

---

### Task 3: Add recommend_papers() to analyzer.py

**Files:**
- Modify: `analyzer.py`
- Modify: `tests/test_analyzer.py`

- [ ] **Step 1: Write failing tests**

Append to the bottom of `tests/test_analyzer.py`:

```python
from analyzer import recommend_papers

SAMPLE_SUMMARIZED = [
    {
        "doi": "10.1109/TPEL.2024.001",
        "title": "Soft-Charging Multiresonant SC Converter for 48V Data Center",
        "venue": "TPEL",
        "year": 2024,
        "citation_count": 12,
        "contribution": "Proposes a multiresonant SC converter with ZCS for all switches.",
        "stars": "⭐⭐",
    },
    {
        "doi": "10.1109/ECCE.2024.002",
        "title": "Control of SC Converters in Data Center Power Distribution",
        "venue": "ECCE",
        "year": 2024,
        "citation_count": 2,
        "contribution": "Presents a digital controller for SC converter arrays.",
        "stars": "⭐",
    },
]

SAMPLE_PROFILE = "Focus: Resonant SC converters for data centers, soft-charging, ZCS."


@patch("analyzer.anthropic.Anthropic")
def test_recommend_papers_returns_tiers(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text='[{"doi": "10.1109/TPEL.2024.001", "tier": "强烈推荐", "reason": "直接推进 RSCC 拓扑"}, {"doi": "10.1109/ECCE.2024.002", "tier": "跳过", "reason": "控制层面工作，非拓扑"}]')]
    )

    result = recommend_papers(SAMPLE_SUMMARIZED, SAMPLE_PROFILE, api_key="sk-ant-test")
    assert len(result) == 2
    assert result[0]["tier"] == "强烈推荐"
    assert result[0]["reason"] == "直接推进 RSCC 拓扑"
    assert result[1]["tier"] == "跳过"
    assert result[1]["reason"] == "控制层面工作，非拓扑"


@patch("analyzer.anthropic.Anthropic")
def test_recommend_papers_preserves_existing_fields(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text='[{"doi": "10.1109/TPEL.2024.001", "tier": "值得一读", "reason": "相关"}, {"doi": "10.1109/ECCE.2024.002", "tier": "跳过", "reason": "不相关"}]')]
    )

    result = recommend_papers(SAMPLE_SUMMARIZED, SAMPLE_PROFILE, api_key="sk-ant-test")
    assert result[0]["title"] == "Soft-Charging Multiresonant SC Converter for 48V Data Center"
    assert result[0]["contribution"] == "Proposes a multiresonant SC converter with ZCS for all switches."
    assert result[0]["stars"] == "⭐⭐"


@patch("analyzer.anthropic.Anthropic")
def test_recommend_papers_empty_input(mock_cls):
    result = recommend_papers([], SAMPLE_PROFILE, api_key="sk-ant-test")
    assert result == []
    mock_cls.return_value.messages.create.assert_not_called()


@patch("analyzer.anthropic.Anthropic")
def test_recommend_papers_falls_back_on_api_error(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.side_effect = Exception("API error")

    result = recommend_papers(SAMPLE_SUMMARIZED, SAMPLE_PROFILE, api_key="sk-ant-test")
    assert len(result) == 2
    assert all(p["tier"] == "值得一读" for p in result)
    assert all(p["reason"] == "" for p in result)
    assert result[0]["title"] == "Soft-Charging Multiresonant SC Converter for 48V Data Center"
```

- [ ] **Step 2: Run new tests to verify they fail**

```bash
python -m pytest tests/test_analyzer.py::test_recommend_papers_returns_tiers tests/test_analyzer.py::test_recommend_papers_empty_input tests/test_analyzer.py::test_recommend_papers_falls_back_on_api_error tests/test_analyzer.py::test_recommend_papers_preserves_existing_fields -v
```

Expected: `ImportError: cannot import name 'recommend_papers' from 'analyzer'`

- [ ] **Step 3: Add recommend_papers() to analyzer.py**

Append to the bottom of `analyzer.py`:

```python
_RECOMMEND_PROMPT = """\
You are helping a power electronics PhD student identify must-read papers each week.

Student research profile:
{research_profile}

Papers this week (already summarized):
{papers_text}

For each paper, assign exactly one tier based on two dimensions:
- Technical impact: venue tier (TPEL/TIE journal papers outrank ECCE/APEC conference papers), citation count, and whether the contribution is novel or incremental
- Personal relevance: match to the student's specific research profile above

Tier definitions:
- "强烈推荐": High technical impact AND directly relevant to the student's research profile
- "值得一读": High technical impact OR relevant to the student's research profile (not both required)
- "跳过": Incremental contribution and low personal relevance

Return a JSON array only — no markdown, no prose, no code fences:
[{{"doi": "<doi>", "tier": "<强烈推荐|值得一读|跳过>", "reason": "<one sentence in Chinese explaining why>"}}]
"""


def recommend_papers(papers: list[dict], research_profile: str, api_key: str) -> list[dict]:
    if not papers:
        return []

    papers_text = "\n\n".join(
        f"DOI: {p['doi']}\nTitle: {p['title']}\nVenue: {p['venue']} {p['stars']}\n"
        f"Summary: {p['contribution']}\nCitations: {p['citation_count']}"
        for p in papers
    )

    client = anthropic.Anthropic(api_key=api_key)
    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": _RECOMMEND_PROMPT.format(
                research_profile=research_profile,
                papers_text=papers_text,
            )}],
        )
        recommendations = json.loads(msg.content[0].text.strip())
    except Exception as e:
        logger.error("Claude recommend failed: %s", e)
        return [{**p, "tier": "值得一读", "reason": ""} for p in papers]

    doi_map = {r["doi"]: r for r in recommendations}
    return [
        {
            **p,
            "tier": doi_map.get(p["doi"], {}).get("tier", "值得一读"),
            "reason": doi_map.get(p["doi"], {}).get("reason", ""),
        }
        for p in papers
    ]
```

- [ ] **Step 4: Run all analyzer tests**

```bash
python -m pytest tests/test_analyzer.py -v
```

Expected: `9 passed`

- [ ] **Step 5: Commit**

```bash
git add analyzer.py tests/test_analyzer.py
git commit -m "feat: add recommend_papers() for personalized must-read scoring"
```

---

### Task 4: Update reporter.py to render recommendation section

**Files:**
- Modify: `reporter.py`
- Modify: `tests/test_reporter.py`

- [ ] **Step 1: Write failing tests**

Append to the bottom of `tests/test_reporter.py`:

```python
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
```

- [ ] **Step 2: Run new tests to verify they fail**

```bash
python -m pytest tests/test_reporter.py::test_build_email_html_shows_recommendation_section tests/test_reporter.py::test_build_email_html_shows_both_tiers tests/test_reporter.py::test_build_email_html_no_rec_section_when_all_skipped tests/test_reporter.py::test_build_email_html_no_rec_section_without_tier_field -v
```

Expected: `FAILED` — `AssertionError: assert '本周推荐' in ...`

- [ ] **Step 3: Update reporter.py**

Replace the entire content of `reporter.py` with:

```python
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def _rec_group_html(papers: list[dict], label: str, color: str) -> str:
    if not papers:
        return ""
    items = "".join(
        f"""<div style="margin-bottom:10px;padding:10px;background:#f9f9f9;border-left:3px solid {color};">
          <p style="margin:0 0 2px 0;font-size:14px;font-weight:bold;">{p['stars']} {p['title']}</p>
          <p style="margin:0 0 2px 0;color:#666;font-size:11px;">{p['venue']} &middot; {p['year']}</p>
          <p style="margin:0;font-size:12px;color:#444;">{p.get('reason', '')}</p>
        </div>"""
        for p in papers
    )
    return f'<p style="margin:12px 0 4px;font-weight:bold;color:{color};">{label}</p>{items}'


def build_email_html(
    new_papers: list[dict],
    trend_text: str,
    db_stats: dict,
    week_label: str,
) -> str:
    must_read  = [p for p in new_papers if p.get("tier") == "强烈推荐"]
    worth_read = [p for p in new_papers if p.get("tier") == "值得一读"]

    if must_read or worth_read:
        rec_html = (
            '<h3 style="color:#0057a8;">&#128218; 本周推荐</h3>'
            + _rec_group_html(must_read,  "强烈推荐", "#c0392b")
            + _rec_group_html(worth_read, "值得一读", "#2980b9")
            + '<hr style="border:none;border-top:1px solid #ddd;margin:24px 0;">'
        )
    else:
        rec_html = ""

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

  {rec_html}

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

- [ ] **Step 4: Run all reporter tests**

```bash
python -m pytest tests/test_reporter.py -v
```

Expected: `7 passed`

- [ ] **Step 5: Commit**

```bash
git add reporter.py tests/test_reporter.py
git commit -m "feat: add recommendation section to weekly email report"
```

---

### Task 5: Wire recommend_papers() into main.py

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

- [ ] **Step 1: Write failing test**

Replace the entire content of `tests/test_main.py` with the version below, which adds the `recommend_papers` mock to `test_run_weekly_sends_email`:

```python
from unittest.mock import patch, MagicMock
from main import run_weekly, run_init


@patch("main.send_email")
@patch("main.analyze_trends", return_value="Direction 1: soft charging.")
@patch("main.recommend_papers")
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
    mock_insert, mock_fetch, mock_enrich, mock_summarize, mock_recommend, mock_trends, mock_send
):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = (10, "2024-01-01T00:00:00")
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=mock_conn)
    ctx.__exit__ = MagicMock(return_value=False)
    mock_connect.return_value = ctx

    paper = {"doi": "10.1109/TPEL.2024.001", "title": "SC Paper", "abstract": "...", "venue": "TPEL", "year": 2024, "citation_count": 0}
    summarized = [{**paper, "contribution": "Great result.", "stars": "⭐⭐"}]
    recommended = [{**summarized[0], "tier": "强烈推荐", "reason": "直接相关"}]

    mock_fetch.return_value = [paper]
    mock_enrich.return_value = [paper]
    mock_summarize.return_value = summarized
    mock_recommend.return_value = recommended

    run_weekly()
    mock_recommend.assert_called_once()
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

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_main.py::test_run_weekly_sends_email -v
```

Expected: `FAILED` — `AssertionError: assert mock_recommend.assert_called_once()` (recommend_papers not called yet)

- [ ] **Step 3: Update main.py**

Change the import line and insert the `recommend_papers` call in `run_weekly()`.

Update the import at line 8 of `main.py` from:

```python
from analyzer import summarize_papers, analyze_trends
```

to:

```python
from analyzer import summarize_papers, analyze_trends, recommend_papers
```

Then in `run_weekly()`, replace:

```python
        summarized = summarize_papers(new_papers, config.ANTHROPIC_API_KEY)
        trend_text = analyze_trends(new_papers, historical, config.ANTHROPIC_API_KEY)
```

with:

```python
        summarized   = summarize_papers(new_papers, config.ANTHROPIC_API_KEY)
        recommended  = recommend_papers(summarized, config.RESEARCH_PROFILE, config.ANTHROPIC_API_KEY)
        trend_text   = analyze_trends(new_papers, historical, config.ANTHROPIC_API_KEY)
```

And replace the `build_email_html` call argument from `summarized` to `recommended`:

```python
    html = build_email_html(
        new_papers=recommended,
        trend_text=trend_text,
        db_stats={"total": total, "since": since_date},
        week_label=_week_label(),
    )
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: All tests pass. (21 tests existed before this plan + 10 added by this plan = 31 total: 4 config + 4 db + 5 fetcher + 9 analyzer + 7 reporter + 2 main)

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: wire recommend_papers into weekly pipeline"
```

---

### Task 6: Smoke test with real credentials

- [ ] **Step 1: Verify .env has all required keys**

Open `.env` and confirm these are set:
- `ANTHROPIC_API_KEY`
- `IEEE_XPLORE_API_KEY` (the new key you just obtained)
- `SENDER_EMAIL`, `SENDER_PASSWORD`, `RECIPIENT_EMAILS`

- [ ] **Step 2: Run --init to seed historical data (first time only)**

If `papers.db` doesn't exist yet, seed 2 years of data:

```bash
cd "C:\Claude_code\Projects\Automation\academic trend"
python main.py --init
```

Expected output ends with: `INFO main: Init complete — stored N papers`

Skip this step if `papers.db` already exists from a prior run.

- [ ] **Step 3: Run a manual weekly report**

```bash
python main.py
```

Expected: email arrives in your inbox with a "📚 本周推荐" section at the top.

- [ ] **Step 4: Confirm all tests still pass**

```bash
python -m pytest tests/ -v
```

Expected: `17 passed`
