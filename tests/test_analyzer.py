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


from analyzer import analyze_trends

HISTORICAL_PAPERS = [
    {"title": "SC Converter 48V Bus 2023", "venue": "TPEL", "year": 2023},
    {"title": "Resonant SC for Rack 2022", "venue": "ECCE", "year": 2022},
]


@patch("analyzer.anthropic.Anthropic")
def test_analyze_trends_returns_text(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="**Evolution:** SC converters have moved from...\n\n**Direction 1:** Soft charging...")]
    )

    result = analyze_trends(SAMPLE_PAPERS, HISTORICAL_PAPERS, api_key="sk-ant-test")
    assert isinstance(result, str)
    assert len(result) > 20


@patch("analyzer.anthropic.Anthropic")
def test_analyze_trends_handles_api_error(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.side_effect = Exception("API error")

    result = analyze_trends(SAMPLE_PAPERS, HISTORICAL_PAPERS, api_key="sk-ant-test")
    assert "unavailable" in result.lower()


from analyzer import recommend_papers

SAMPLE_SUMMARIZED = [
    {
        "doi": "10.1109/TPEL.2024.001",
        "title": "Soft-Charging Multiresonant SC Converter for 48V Data Center",
        "venue": "TPEL",
        "year": 2024,
        "citation_count": 12,
        "contribution": "Proposes a multiresonant SC converter with ZCS for all switches.",
        "stars": "⭐⭐",
    },
    {
        "doi": "10.1109/ECCE.2024.002",
        "title": "Control of SC Converters in Data Center Power Distribution",
        "venue": "ECCE",
        "year": 2024,
        "citation_count": 2,
        "contribution": "Presents a digital controller for SC converter arrays.",
        "stars": "⭐",
    },
]

SAMPLE_PROFILE = "Focus: Resonant SC converters for data centers, soft-charging, ZCS."


@patch("analyzer.anthropic.Anthropic")
def test_recommend_papers_returns_tiers(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text='[{"doi": "10.1109/TPEL.2024.001", "tier": "强烈推荐", "reason": "直接推进 RSCC 拓扑"}, {"doi": "10.1109/ECCE.2024.002", "tier": "跳过", "reason": "控制层面工作，非拓扑"}]')]
    )

    result = recommend_papers(SAMPLE_SUMMARIZED, SAMPLE_PROFILE, api_key="sk-ant-test")
    assert len(result) == 2
    assert result[0]["tier"] == "强烈推荐"
    assert result[0]["reason"] == "直接推进 RSCC 拓扑"
    assert result[1]["tier"] == "跳过"
    assert result[1]["reason"] == "控制层面工作，非拓扑"


@patch("analyzer.anthropic.Anthropic")
def test_recommend_papers_preserves_existing_fields(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text='[{"doi": "10.1109/TPEL.2024.001", "tier": "值得一读", "reason": "相关"}, {"doi": "10.1109/ECCE.2024.002", "tier": "跳过", "reason": "不相关"}]')]
    )

    result = recommend_papers(SAMPLE_SUMMARIZED, SAMPLE_PROFILE, api_key="sk-ant-test")
    assert result[0]["title"] == "Soft-Charging Multiresonant SC Converter for 48V Data Center"
    assert result[0]["contribution"] == "Proposes a multiresonant SC converter with ZCS for all switches."
    assert result[0]["stars"] == "⭐⭐"


@patch("analyzer.anthropic.Anthropic")
def test_recommend_papers_empty_input(mock_cls):
    result = recommend_papers([], SAMPLE_PROFILE, api_key="sk-ant-test")
    assert result == []
    mock_cls.return_value.messages.create.assert_not_called()


@patch("analyzer.anthropic.Anthropic")
def test_recommend_papers_falls_back_on_api_error(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.side_effect = Exception("API error")

    result = recommend_papers(SAMPLE_SUMMARIZED, SAMPLE_PROFILE, api_key="sk-ant-test")
    assert len(result) == 2
    assert all(p["tier"] == "值得一读" for p in result)
    assert all(p["reason"] == "" for p in result)
    assert result[0]["title"] == "Soft-Charging Multiresonant SC Converter for 48V Data Center"
