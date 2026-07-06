import os
from dotenv import load_dotenv

load_dotenv()

# =====================================================================
# USER SETTINGS — edit this section to customise the tool
# =====================================================================

# Who receives the weekly digest
RECIPIENT_EMAILS: list[str] = [
    "ccsummerikk@gmail.com",
]

# Papers must contain at least ONE topic keyword (these are alternative
# phrasings of the same subject). If KEYWORDS_CONTEXT is non-empty, papers must
# ALSO contain at least one context keyword; leave it empty to track the whole
# topic area without an application filter.
KEYWORDS_TOPIC: list[str] = [
    "switched capacitor",
    "switched-capacitor",
    "resonant switched capacitor",
    "hybrid resonant converter",
]
KEYWORDS_CONTEXT: list[str] = []

# IEEE venues to monitor (abbreviation → exact IEEE publication title)
VENUES: dict[str, str] = {
    "TPEL": "IEEE Transactions on Power Electronics",
    "TIE":  "IEEE Transactions on Industrial Electronics",
    "ECCE": "IEEE Energy Conversion Congress and Exposition",
    "APEC": "IEEE Applied Power Electronics Conference and Exposition",
    "JESTPE": "IEEE Journal of Emerging and Selected Topics in Power Electronics",
    "OJPEL":  "IEEE Open Journal of Power Electronics",
}

# Your research profile — used by the AI to rank paper relevance
RESEARCH_PROFILE: str = """
Focus: Resonant and soft-switching switched capacitor converters (RSCC) for 48V data center power delivery.
Key interests:
- Soft-charging / ZCS operation in SC topologies (SSL/FSL modeling framework)
- Multi-phase resonant SC converter design and analysis
- Flying-capacitor multilevel and Dickson-based topologies
- Pilawa-Podgurski group publications
- Topology derivation and extension methods
Prioritize papers that advance circuit-level analysis or introduce new topologies over system-level/application papers.
"""

# =====================================================================
# SYSTEM SETTINGS — no need to change these normally
# =====================================================================

GEMINI_API_KEY: str = os.environ["GEMINI_API_KEY"]
IEEE_XPLORE_API_KEY: str = os.environ["IEEE_XPLORE_API_KEY"]

SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL: str = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD: str = os.environ["SENDER_PASSWORD"]

LOOKBACK_DAYS: int = int(os.getenv("LOOKBACK_DAYS", "30"))
HISTORY_YEARS: int = int(os.getenv("HISTORY_YEARS", "2"))
DB_PATH: str = os.getenv("DB_PATH", "papers.db")
IEEE_API_BASE: str = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
