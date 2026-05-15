import pytest
from unittest.mock import patch, MagicMock
from fetcher import fetch_papers_ieee

MOCK_IEEE_RESPONSE = {
    "total_records": 2,
    "articles": [
        {
            "doi": "10.1109/TPEL.2024.001",
            "title": "Switched-Capacitor Converter for 48V Data Center",
            "abstract": "This paper proposes a 2-phase SC converter...",
            "publication_title": "IEEE Transactions on Power Electronics",
            "publication_year": 2024,
        },
        {
            "doi": "10.1109/TIE.2024.002",
            "title": "Resonant SC Topology for Server Rack",
            "abstract": "We present a resonant SC converter...",
            "publication_title": "IEEE Transactions on Industrial Electronics",
            "publication_year": 2024,
        },
    ],
}


@patch("fetcher.requests.get")
def test_fetch_papers_ieee_returns_papers(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_IEEE_RESPONSE
    mock_get.return_value = mock_resp

    papers = fetch_papers_ieee(start_date="20240101", end_date="20240108", api_key="test-key")
    assert len(papers) == 2
    assert papers[0]["doi"] == "10.1109/TPEL.2024.001"
    assert papers[0]["venue"] == "TPEL"
    assert papers[1]["venue"] == "TPEL"


@patch("fetcher.requests.get")
def test_fetch_papers_ieee_handles_empty(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"total_records": 0, "articles": []}
    mock_get.return_value = mock_resp

    papers = fetch_papers_ieee(start_date="20240101", end_date="20240108", api_key="test-key")
    assert papers == []


@patch("fetcher.requests.get")
def test_fetch_papers_ieee_handles_api_error(mock_get):
    mock_get.side_effect = Exception("Connection timeout")
    papers = fetch_papers_ieee(start_date="20240101", end_date="20240108", api_key="test-key")
    assert papers == []
