from unittest.mock import MagicMock, patch


def _make_mock_client(response_json: str):
    mock_content = MagicMock()
    mock_content.text = response_json
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client


def test_detect_clips_returns_sorted_by_score():
    response_json = '''[
        {"start_time": 10.0, "end_time": 50.0, "title": "Momento incrível", "virality_score": 75, "reasons": ["Gancho forte", "Emoção intensa"]},
        {"start_time": 60.0, "end_time": 110.0, "title": "Top moment", "virality_score": 90, "reasons": ["Alta retenção"]}
    ]'''
    mock_client = _make_mock_client(response_json)
    with patch("app.integrations.claude.get_claude_client", return_value=mock_client):
        from app.integrations.claude import detect_clips
        result = detect_clips([{"start": 10.0, "end": 50.0, "text": "hello"}], "hello")
    assert len(result) == 2
    assert result[0]["virality_score"] == 90
    assert result[1]["virality_score"] == 75
    assert result[0]["title"] == "Top moment"


def test_detect_clips_clamps_score():
    response_json = '[{"start_time": 0.0, "end_time": 45.0, "title": "Test", "virality_score": 150, "reasons": ["x"]}]'
    mock_client = _make_mock_client(response_json)
    with patch("app.integrations.claude.get_claude_client", return_value=mock_client):
        from app.integrations.claude import detect_clips
        result = detect_clips([], "text")
    assert result[0]["virality_score"] == 100


def test_detect_clips_truncates_title():
    long_title = "A" * 100
    response_json = f'[{{"start_time": 0.0, "end_time": 45.0, "title": "{long_title}", "virality_score": 50, "reasons": ["x"]}}]'
    mock_client = _make_mock_client(response_json)
    with patch("app.integrations.claude.get_claude_client", return_value=mock_client):
        from app.integrations.claude import detect_clips
        result = detect_clips([], "text")
    assert len(result[0]["title"]) <= 60
