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
