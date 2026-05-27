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
KEYWORDS: list[str] = KEYWORDS_REQUIRED + KEYWORDS_CONTEXT  # For backward compatibility

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
Focus: Resonant and soft-switching switched capacitor converters (RSCC) for 48V data center power delivery.
Key interests:
- Soft-charging / ZCS operation in SC topologies (SSL/FSL modeling framework)
- Multi-phase resonant SC converter design and analysis
- Flying-capacitor multilevel and Dickson-based topologies
- Pilawa-Podgurski group publications
- Topology derivation and extension methods
Prioritize papers that advance circuit-level analysis or introduce new topologies over system-level/application papers.
""")
