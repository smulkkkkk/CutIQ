import pytest
from unittest.mock import patch, MagicMock


def test_extract_audio_calls_ffmpeg():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        from app.integrations.ffmpeg import extract_audio
        extract_audio("/tmp/video.mp4", "/tmp/audio.wav")

    call_args = mock_run.call_args[0][0]  # first positional arg = command list
    assert "ffmpeg" in call_args[0]
    assert "/tmp/video.mp4" in call_args
    assert "/tmp/audio.wav" in call_args


def test_extract_audio_raises_on_ffmpeg_error():
    import subprocess
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")
        from app.integrations.ffmpeg import extract_audio
        with pytest.raises(RuntimeError, match="FFmpeg"):
            extract_audio("/tmp/video.mp4", "/tmp/audio.wav")
