from unittest.mock import MagicMock, patch, ANY

def test_generate_presigned_upload_url():
    mock_client = MagicMock()
    mock_client.generate_presigned_url.return_value = "https://r2.example.com/upload?sig=abc"
    with patch("app.integrations.r2._get_r2_client", return_value=mock_client):
        from app.integrations.r2 import generate_presigned_upload_url
        url = generate_presigned_upload_url("videos/user/proj/video.mp4")
    mock_client.generate_presigned_url.assert_called_once_with(
        "put_object",
        Params={"Bucket": ANY, "Key": "videos/user/proj/video.mp4", "ContentType": "video/mp4"},
        ExpiresIn=3600,
    )
    assert url == "https://r2.example.com/upload?sig=abc"

def test_generate_presigned_download_url():
    mock_client = MagicMock()
    mock_client.generate_presigned_url.return_value = "https://r2.example.com/dl?sig=xyz"
    with patch("app.integrations.r2._get_r2_client", return_value=mock_client):
        from app.integrations.r2 import generate_presigned_download_url
        url = generate_presigned_download_url("videos/user/proj/video.mp4")
    assert url == "https://r2.example.com/dl?sig=xyz"

def test_download_to_path():
    mock_client = MagicMock()
    with patch("app.integrations.r2._get_r2_client", return_value=mock_client):
        from app.integrations.r2 import download_to_path
        download_to_path("videos/video.mp4", "/tmp/video.mp4")
    mock_client.download_file.assert_called_once_with(ANY, "videos/video.mp4", "/tmp/video.mp4")

def test_upload_from_path():
    mock_client = MagicMock()
    with patch("app.integrations.r2._get_r2_client", return_value=mock_client):
        from app.integrations.r2 import upload_from_path
        upload_from_path("/tmp/video.mp4", "clips/clip.mp4", "video/mp4")
    mock_client.upload_file.assert_called_once_with(
        "/tmp/video.mp4", ANY, "clips/clip.mp4", ExtraArgs={"ContentType": "video/mp4"}
    )
