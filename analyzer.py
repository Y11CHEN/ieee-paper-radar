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
