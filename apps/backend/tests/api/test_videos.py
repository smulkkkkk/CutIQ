import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from app.main import app
from app.api.deps import get_current_user

NOW = datetime(2026, 7, 3, tzinfo=timezone.utc)
MOCK_USER = MagicMock(id="user-1", email="test@example.com")
MOCK_PROJECT = MagicMock(id="proj-1", user_id="user-1", title="My Video", status="created")
MOCK_VIDEO = MagicMock(
    id="vid-1", project_id="proj-1", user_id="user-1",
    source_type="upload", filename="video.mp4", status="pending",
    source_url=None, r2_key="videos/user-1/proj-1/vid-1/video.mp4",
    duration_seconds=None, size_bytes=None,
    created_at=NOW,
)


@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_video_presigned_url(client):
    with patch("app.api.routes.videos.ProjectRepository") as mock_proj_cls, \
         patch("app.api.routes.videos.VideoRepository") as mock_vid_cls, \
         patch("app.api.routes.videos.generate_presigned_upload_url") as mock_presigned:
        mock_proj_cls.return_value.get_by_id.return_value = MOCK_PROJECT
        mock_vid_cls.return_value.create.return_value = MOCK_VIDEO
        mock_presigned.return_value = "https://r2.example.com/upload?sig=abc"
        response = await client.post("/api/videos", json={
            "project_id": "proj-1",
            "filename": "video.mp4",
        })
    assert response.status_code == 201
    data = response.json()
    assert "video_id" in data
    assert data["video_id"] == "vid-1"
    assert "upload_url" in data
    assert data["upload_url"] == "https://r2.example.com/upload?sig=abc"


@pytest.mark.asyncio
async def test_create_video_project_not_found(client):
    with patch("app.api.routes.videos.ProjectRepository") as mock_proj_cls:
        mock_proj_cls.return_value.get_by_id.return_value = None
        response = await client.post("/api/videos", json={
            "project_id": "missing",
            "filename": "video.mp4",
        })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_process_video(client):
    with patch("app.api.routes.videos.VideoRepository") as mock_vid_cls, \
         patch("app.api.routes.videos.JobRepository") as mock_job_cls, \
         patch("app.api.routes.videos.enqueue_transcription") as mock_enqueue:
        mock_vid_cls.return_value.get_by_id.return_value = MOCK_VIDEO
        mock_enqueue.return_value = "arq-job-123"
        response = await client.post("/api/videos/vid-1/process")
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["job_id"] == "arq-job-123"
