import json
import logging
import anthropic

logger = logging.getLogger(__name__)

_SUMMARIZE_PROMPT = """\
You are a power electronics research assistant. Summarize each paper below.

Return a JSON array only — no markdown, no prose, no code fences. One object per paper:
{{"doi": "<doi>", "contribution": "<2-3 sentences: what was done, what gap it fills, key result>", "stars": "<⭐⭐ for TPEL/TIE journal papers, ⭐ for ECCE/APEC conference papers>"}}

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
            {**p, "contribution": "Summary unavailable.", "stars": "⭐⭐" if p["venue"] in ("TPEL", "TIE") else "⭐"}
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
