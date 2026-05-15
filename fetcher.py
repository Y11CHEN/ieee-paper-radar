import logging
import time
import requests
from config import IEEE_API_BASE, VENUES, KEYWORDS

logger = logging.getLogger(__name__)


def fetch_papers_ieee(start_date: str, end_date: str, api_key: str) -> list[dict]:
    """Fetch papers from IEEE Xplore for all configured venues."""
    all_papers: list[dict] = []
    seen_dois: set[str] = set()
    query_terms = " OR ".join(f'"{k}"' for k in KEYWORDS)
    query = f"({query_terms})"

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
                    if doi in seen_dois:
                        continue
                    seen_dois.add(doi)
                    all_papers.append({
                        "doi": doi,
                        "title": a.get("title", ""),
                        "abstract": a.get("abstract", ""),
                        "venue": abbrev,
                        "year": int(a.get("publication_year", 0)),
                        "citation_count": 0,
                    })
                total = int(data.get("total_records", len(articles)))
                if start_record + len(articles) - 1 >= total or not articles:
                    break
                start_record += len(articles)
            except Exception as e:
                logger.error("IEEE Xplore fetch failed for %s: %s", abbrev, e)
                break

    return all_papers


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
