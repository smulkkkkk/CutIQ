import pytest
from unittest.mock import patch, MagicMock


def test_transcribe_returns_segments():
    mock_segment = MagicMock()
    mock_segment.start = 0.0
    mock_segment.end = 5.0
    mock_segment.text = " Hello world"

    mock_info = MagicMock()
    mock_info.language = "en"

    mock_model = MagicMock()
    mock_model.transcribe.return_value = ([mock_segment], mock_info)

    with patch("app.integrations.whisper.WhisperModel", return_value=mock_model):
        from app.integrations import whisper as whisper_module
        whisper_module._client = None
        client = whisper_module.get_whisper_client()
        result = client.transcribe("audio.wav")

    assert result["language"] == "en"
    assert len(result["segments"]) == 1
    assert result["segments"][0]["text"] == " Hello world"
    assert " Hello world" in result["text"]
