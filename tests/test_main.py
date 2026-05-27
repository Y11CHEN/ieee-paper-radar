from unittest.mock import patch, MagicMock
from main import run_weekly, run_init


@patch("main.send_email")
@patch("main.analyze_trends", return_value="Direction 1: soft charging.")
@patch("main.recommend_papers")
@patch("main.summarize_papers")
@patch("main.enrich_with_semantic_scholar")
@patch("main.fetch_papers_ieee")
@patch("main.insert_papers")
@patch("main.get_recent_papers", return_value=[])
@patch("main.get_known_dois", return_value=set())
@patch("main.init_db")
@patch("main.sqlite3.connect")
def test_run_weekly_sends_email(
    mock_connect, mock_init_db, mock_known, mock_recent,
    mock_insert, mock_fetch, mock_enrich, mock_summarize, mock_recommend, mock_trends, mock_send
):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = (10, "2024-01-01T00:00:00")
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=mock_conn)
    ctx.__exit__ = MagicMock(return_value=False)
    mock_connect.return_value = ctx

    paper = {"doi": "10.1109/TPEL.2024.001", "title": "SC Paper", "abstract": "...", "venue": "TPEL", "year": 2024, "citation_count": 0}
    summarized = [{**paper, "contribution": "Great result.", "stars": "⭐⭐"}]
    recommended = [{**summarized[0], "tier": "强烈推荐", "reason": "直接相关"}]

    mock_fetch.return_value = [paper]
    mock_enrich.return_value = [paper]
    mock_summarize.return_value = summarized
    mock_recommend.return_value = recommended

    run_weekly()
    mock_recommend.assert_called_once()
    mock_send.assert_called_once()


@patch("main.insert_papers")
@patch("main.enrich_with_semantic_scholar", return_value=[])
@patch("main.fetch_papers_ieee", return_value=[])
@patch("main.get_known_dois", return_value=set())
@patch("main.init_db")
@patch("main.sqlite3.connect")
def test_run_init_does_not_send_email(mock_connect, mock_init, mock_known, mock_fetch, mock_enrich, mock_insert):
    mock_conn = MagicMock()
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=mock_conn)
    ctx.__exit__ = MagicMock(return_value=False)
    mock_connect.return_value = ctx

    with patch("main.send_email") as mock_send:
        run_init()
        mock_send.assert_not_called()
