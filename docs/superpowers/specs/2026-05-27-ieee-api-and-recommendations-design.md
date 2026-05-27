# SC Research Weekly — IEEE API Integration & Paper Recommendation Design Spec

**Date:** 2026-05-27
**Topic:** Fix query logic bugs, integrate IEEE Xplore API properly, add personalized must-read recommendations
**Status:** Approved

---

## Overview

Two parallel goals:

1. **Fix three bugs** in the existing pipeline that would silently degrade result quality: OR query logic, incorrect conference publication names, and a too-short lookback window.
2. **Add `recommend_papers()`** — a new Claude API call that scores each paper on technical impact and personal relevance, then renders a "本周推荐" section at the top of the weekly email.

---

## Bug Fixes

### Fix 1 — Query logic: OR → AND (`config.py`, `fetcher.py`)

**Problem:** Current code builds `("switched capacitor" OR "data center" OR "48V bus" OR "rack power")`. This fetches papers about pure data-center networking or unrelated capacitor topics.

**Fix:** Split `KEYWORDS` into two config lists:

```python
KEYWORDS_REQUIRED: list[str] = ["switched capacitor"]
KEYWORDS_CONTEXT: list[str] = ["data center", "48V bus", "rack power", "server rack"]
```

`fetcher.py` builds:
```python
required = " AND ".join(f'"{k}"' for k in KEYWORDS_REQUIRED)
context  = " OR ".join(f'"{k}"' for k in KEYWORDS_CONTEXT)
query    = f"({required}) AND ({context})"
```

Result: `("switched capacitor") AND ("data center" OR "48V bus" OR "rack power" OR "server rack")`

### Fix 2 — Conference publication names (`config.py`)

**Problem:** "Energy Conversion Congress" and "Applied Power Electronics Conference" are partial names that may not match IEEE Xplore's `publication_title` field exactly.

**Fix:**
```python
VENUES: dict[str, str] = {
    "TPEL": "IEEE Transactions on Power Electronics",
    "TIE":  "IEEE Transactions on Industrial Electronics",
    "ECCE": "IEEE Energy Conversion Congress and Exposition",
    "APEC": "IEEE Applied Power Electronics Conference and Exposition",
}
```

### Fix 3 — Lookback window: 7 → 14 days (`config.py`)

**Problem:** IEEE Xplore indexes new papers with a 7–14 day delay. A strict 7-day window risks missing recently published papers.

**Fix:** Change default to 14 days. The existing `get_known_dois()` deduplication in `main.py` prevents any paper from being processed twice.

```python
LOOKBACK_DAYS: int = int(os.getenv("LOOKBACK_DAYS", "14"))
```

---

## New Feature: Personalized Paper Recommendations

### Research Profile in `config.py`

```python
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

Overridable via environment variable for future research direction changes.

### `recommend_papers()` in `analyzer.py`

**Signature:**
```python
def recommend_papers(papers: list[dict], research_profile: str, api_key: str) -> list[dict]:
```

**Input:** List of papers already processed by `summarize_papers()` — each has `doi`, `title`, `venue`, `stars`, `contribution`, `citation_count`.

**Output:** Same list with two new fields added to each paper:
- `tier`: `"强烈推荐"` | `"值得一读"` | `"跳过"`
- `reason`: one-sentence explanation

**Tier definitions:**

| Tier | Criteria |
|------|----------|
| 强烈推荐 | High technical impact **AND** directly relevant to research profile |
| 值得一读 | High technical impact **OR** relevant to research profile (not both) |
| 跳过 | Incremental contribution and low personal relevance |

No quantity cap — all "强烈推荐" and "值得一读" papers surface in the recommendation section.

**Failure mode:** If Claude API fails, all papers default to `tier = "值得一读"`, `reason = ""`. Pipeline does not crash.

### `main.py` wiring

```python
summarized  = summarize_papers(new_papers, config.ANTHROPIC_API_KEY)
recommended = recommend_papers(summarized, config.RESEARCH_PROFILE, config.ANTHROPIC_API_KEY)
trend_text  = analyze_trends(new_papers, historical, config.ANTHROPIC_API_KEY)
```

`build_email_html()` receives `recommended` in place of `summarized`. Function signature unchanged.

---

## Email Layout

```
[SC Research Weekly] 2026-W22 | 5 new papers

📚 本周推荐
  ── 强烈推荐 ──────────────────────────────
  ⭐⭐ A Soft-Switching Multiresonant...  (TPEL)
  理由：直接推进 RSCC 拓扑推导方法...

  ── 值得一读 ──────────────────────────────
  ⭐ Flying Capacitor Multilevel...  (ECCE)
  理由：与你关注的 FC 拓扑相关...

── 所有新论文（5 篇）──────────────────────
  [1] ⭐⭐ Title — TPEL · 2026 · Citations: 3
      Contribution: ...
  [2] ...

── 研究趋势分析 ────────────────────────────
  Evolution Narrative: ...
  Direction 1: ...
  Direction 2: ...
  Direction 3: ...

── 数据库统计 ──────────────────────────────
  42 papers · TPEL, TIE, ECCE, APEC · Since 2024-01-01
```

"本周推荐" section is omitted entirely if all papers are tiered "跳过".

---

## Files Changed

| File | Change |
|------|--------|
| `config.py` | Split KEYWORDS, fix VENUES names, LOOKBACK_DAYS=14, add RESEARCH_PROFILE |
| `fetcher.py` | Rebuild query with AND logic from KEYWORDS_REQUIRED / KEYWORDS_CONTEXT |
| `analyzer.py` | Add `recommend_papers()` |
| `reporter.py` | `build_email_html()` renders "本周推荐" section from `tier` field |
| `main.py` | Insert `recommend_papers()` call between summarize and trend |
| `tests/test_analyzer.py` | Add tests for `recommend_papers()` |
| `tests/test_reporter.py` | Add tests for recommendation section rendering |

---

## Out of Scope

- Quantitative trend metrics (keyword frequency over time, citation growth charts)
- Non-IEEE venues (arXiv, Nature Energy, etc.)
- Persistent storage of recommendation history
- Web UI or dashboard
