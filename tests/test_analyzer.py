import pytest
from unittest.mock import MagicMock, patch
from analyzer import summarize_papers

SAMPLE_PAPERS = [
    {
        "doi": "10.1109/TPEL.2024.001",
        "title": "High-Efficiency Switched-Capacitor Converter for 48V Data Center",
        "abstract": "This paper presents a novel 2-phase SC converter achieving 98.5% efficiency...",
        "venue": "TPEL",
        "year": 2024,
        "citation_count": 5,
    }
]


@patch("analyzer.anthropic.Anthropic")
def test_summarize_papers_returns_summaries(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text='[{"doi": "10.1109/TPEL.2024.001", "contribution": "Proposes a 2-phase SC converter with 98.5% efficiency for 48V data center bus.", "stars": "⭐⭐"}]')]
    )

    result = summarize_papers(SAMPLE_PAPERS, api_key="sk-ant-test")
    assert len(result) == 1
    assert result[0]["doi"] == "10.1109/TPEL.2024.001"
    assert "contribution" in result[0]
    assert result[0]["stars"] in ("⭐", "⭐⭐")


@patch("analyzer.anthropic.Anthropic")
def test_summarize_papers_empty_input(mock_cls):
    result = summarize_papers([], api_key="sk-ant-test")
    assert result == []
    mock_cls.return_value.messages.create.assert_not_called()


@patch("analyzer.anthropic.Anthropic")
def test_summarize_papers_falls_back_on_api_error(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.side_effect = Exception("API error")

    result = summarize_papers(SAMPLE_PAPERS, api_key="sk-ant-test")
    assert len(result) == 1
    assert result[0]["contribution"] == "Summary unavailable."
