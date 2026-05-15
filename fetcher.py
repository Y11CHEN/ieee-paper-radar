import logging
import requests
from config import IEEE_API_BASE, VENUES

logger = logging.getLogger(__name__)

_VENUE_LOOKUP: dict[str, str] = {full.lower(): abbrev for abbrev, full in VENUES.items()}


def _match_venue(publication_title: str) -> str:
    title_lower = publication_title.lower()
    for fragment, abbrev in _VENUE_LOOKUP.items():
        if fragment in title_lower:
            return abbrev
    return publication_title[:10]


def fetch_papers_ieee(start_date: str, end_date: str, api_key: str) -> list[dict]:
    """Fetch papers from IEEE Xplore for all configured venues."""
    all_papers: list[dict] = []
    seen_dois: set[str] = set()
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
                    if doi in seen_dois:
                        continue
                    seen_dois.add(doi)
                    pub_title_article = a.get("publication_title", "")
                    venue = _match_venue(pub_title_article) if pub_title_article else abbrev
                    all_papers.append({
                        "doi": doi,
                        "title": a.get("title", ""),
                        "abstract": a.get("abstract", ""),
                        "venue": venue,
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
