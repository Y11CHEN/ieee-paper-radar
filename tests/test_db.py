import sqlite3
import pytest
from datetime import datetime
from db import init_db, insert_papers, get_known_dois, get_recent_papers


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    init_db(c)
    yield c
    c.close()


def test_init_creates_table(conn):
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='papers'")
    assert cursor.fetchone() is not None


def test_insert_and_get_known_dois(conn):
    papers = [
        {"doi": "10.1109/TPEL.2024.001", "title": "Paper A", "abstract": "...", "venue": "TPEL", "year": 2024, "citation_count": 3},
        {"doi": "10.1109/TPEL.2024.002", "title": "Paper B", "abstract": "...", "venue": "TPEL", "year": 2024, "citation_count": 0},
    ]
    insert_papers(conn, papers)
    dois = get_known_dois(conn)
    assert "10.1109/TPEL.2024.001" in dois
    assert "10.1109/TPEL.2024.002" in dois


def test_insert_ignores_duplicates(conn):
    paper = {"doi": "10.1109/TPEL.2024.001", "title": "Paper A", "abstract": "...", "venue": "TPEL", "year": 2024, "citation_count": 0}
    insert_papers(conn, [paper])
    insert_papers(conn, [paper])
    dois = get_known_dois(conn)
    assert len([d for d in dois if d == "10.1109/TPEL.2024.001"]) == 1


def test_get_recent_papers(conn):
    current_year = datetime.now().year
    papers = [
        {"doi": "10.1109/TPEL.2024.001", "title": "Recent Paper", "abstract": "SC for DC", "venue": "TPEL", "year": current_year, "citation_count": 3},
        {"doi": "10.1109/TPEL.2020.001", "title": "Old Paper", "abstract": "Old work", "venue": "TPEL", "year": current_year - 5, "citation_count": 50},
    ]
    insert_papers(conn, papers)
    recent = get_recent_papers(conn, years=2)
    dois = [p["doi"] for p in recent]
    assert "10.1109/TPEL.2024.001" in dois
    assert "10.1109/TPEL.2020.001" not in dois
