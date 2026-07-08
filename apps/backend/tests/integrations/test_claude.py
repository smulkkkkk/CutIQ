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


def test_detect_clips_parses_five_clips():
    response_json = '''[
        {"start_time": 5.0, "end_time": 55.0, "title": "Clip 1", "virality_score": 90, "reasons": ["Forte abertura", "Gatilho emocional"]},
        {"start_time": 60.0, "end_time": 110.0, "title": "Clip 2", "virality_score": 75, "reasons": ["Informação valiosa"]},
        {"start_time": 120.0, "end_time": 185.0, "title": "Clip 3", "virality_score": 82, "reasons": ["Momento de virada", "Climax narrativo"]},
        {"start_time": 200.0, "end_time": 260.0, "title": "Clip 4", "virality_score": 68, "reasons": ["Humor natural"]},
        {"start_time": 300.0, "end_time": 360.0, "title": "Clip 5", "virality_score": 95, "reasons": ["Conclusão impactante", "Call to action forte", "Alta retenção"]}
    ]'''
    mock_client = _make_mock_client(response_json)
    with patch("app.integrations.claude.get_claude_client", return_value=mock_client):
        from app.integrations.claude import detect_clips
        result = detect_clips([{"start": 5.0, "end": 55.0, "text": "hello"}], "hello")
    assert len(result) == 5
    assert result[0]["virality_score"] == 95   # sorted by score desc
    assert result[0]["title"] == "Clip 5"
    assert all(k in result[0] for k in ("start_time", "end_time", "title", "virality_score", "reasons"))
    assert isinstance(result[0]["reasons"], list)
