from unittest.mock import MagicMock, patch


def _mock_supabase(signed_url: str = "https://supabase.example.com/storage/signed"):
    mock_result = MagicMock()
    mock_result.signed_url = signed_url
    mock_bucket = MagicMock()
    mock_bucket.create_signed_upload_url.return_value = mock_result
    mock_bucket.create_signed_url.return_value = mock_result
    mock_client = MagicMock()
    mock_client.storage.from_.return_value = mock_bucket
    return mock_client, mock_bucket


def test_generate_presigned_upload_url():
    mock_client, mock_bucket = _mock_supabase("https://supabase.example.com/upload")
    with patch("app.integrations.r2.get_supabase", return_value=mock_client):
        from app.integrations.r2 import generate_presigned_upload_url
        url = generate_presigned_upload_url("videos/user/proj/video.mp4")
    mock_bucket.create_signed_upload_url.assert_called_once_with("videos/user/proj/video.mp4")
    assert url == "https://supabase.example.com/upload"


def test_generate_presigned_download_url():
    mock_client, mock_bucket = _mock_supabase("https://supabase.example.com/download")
    with patch("app.integrations.r2.get_supabase", return_value=mock_client):
        from app.integrations.r2 import generate_presigned_download_url
        url = generate_presigned_download_url("videos/user/proj/video.mp4", expires_in=7200)
    mock_bucket.create_signed_url.assert_called_once_with("videos/user/proj/video.mp4", 7200)
    assert url == "https://supabase.example.com/download"


def test_download_to_path(tmp_path):
    mock_client, mock_bucket = _mock_supabase()
    mock_bucket.download.return_value = b"fake video bytes"
    dest = tmp_path / "video.mp4"
    with patch("app.integrations.r2.get_supabase", return_value=mock_client):
        from app.integrations.r2 import download_to_path
        download_to_path("videos/video.mp4", str(dest))
    mock_bucket.download.assert_called_once_with("videos/video.mp4")
    assert dest.read_bytes() == b"fake video bytes"


def test_upload_from_path(tmp_path):
    mock_client, mock_bucket = _mock_supabase()
    src = tmp_path / "video.mp4"
    src.write_bytes(b"fake video bytes")
    with patch("app.integrations.r2.get_supabase", return_value=mock_client):
        from app.integrations.r2 import upload_from_path
        upload_from_path(str(src), "clips/clip.mp4", "video/mp4")
    mock_bucket.upload.assert_called_once_with("clips/clip.mp4", b"fake video bytes", {"content-type": "video/mp4"})
