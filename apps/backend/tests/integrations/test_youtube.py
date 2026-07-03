from unittest.mock import MagicMock, patch

MOCK_INFO = {
    "title": "Test Video",
    "duration": 120,
    "thumbnail": "https://img.youtube.com/thumb.jpg",
    "ext": "mp4",
}

def test_get_youtube_info():
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = lambda s: s
    mock_ydl.__exit__ = MagicMock(return_value=False)
    mock_ydl.extract_info.return_value = MOCK_INFO

    with patch("yt_dlp.YoutubeDL", return_value=mock_ydl):
        from app.integrations.youtube import get_youtube_info
        info = get_youtube_info("https://youtube.com/watch?v=abc")

    assert info["title"] == "Test Video"
    assert info["duration"] == 120.0
    assert "thumbnail" in info

def test_download_youtube_to_r2():
    import os
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = lambda s: s
    mock_ydl.__exit__ = MagicMock(return_value=False)
    mock_ydl.extract_info.return_value = MOCK_INFO
    mock_ydl.prepare_filename.return_value = "/tmp/fakedir/Test Video.mp4"

    with patch("yt_dlp.YoutubeDL", return_value=mock_ydl), \
         patch("app.integrations.youtube.upload_from_path") as mock_upload, \
         patch("tempfile.TemporaryDirectory") as mock_tmpdir, \
         patch("os.listdir", return_value=["Test Video.mp4"]):
        mock_tmpdir.return_value.__enter__ = lambda s: "/tmp/fakedir"
        mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)
        from app.integrations.youtube import download_youtube_to_r2
        result = download_youtube_to_r2("https://youtube.com/watch?v=abc", "videos/user/proj/video.mp4")

    mock_upload.assert_called_once()
    assert result["title"] == "Test Video"
    assert result["duration"] == 120.0
