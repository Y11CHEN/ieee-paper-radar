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
