import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

NOW = datetime(2026, 7, 3, tzinfo=timezone.utc).isoformat()

MOCK_PROJECT_ROW = {
    "id": "proj-1",
    "user_id": "user-1",
    "title": "My Video",
    "status": "created",
    "created_at": NOW,
    "updated_at": NOW,
}

MOCK_VIDEO_ROW = {
    "id": "vid-1",
    "project_id": "proj-1",
    "user_id": "user-1",
    "source_type": "upload",
    "filename": "video.mp4",
    "status": "pending",
    "source_url": None,
    "r2_key": "videos/user-1/proj-1/vid-1/video.mp4",
    "duration_seconds": None,
    "size_bytes": None,
    "created_at": NOW,
}


def test_project_create():
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value.data = [MOCK_PROJECT_ROW]
    with patch("app.repositories.projects.get_supabase", return_value=mock_sb):
        from app.repositories.projects import ProjectRepository
        repo = ProjectRepository()
        project = repo.create("user-1", "My Video")
    assert project.id == "proj-1"
    assert project.title == "My Video"
    assert project.status == "created"


def test_project_get_by_id():
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = MOCK_PROJECT_ROW
    with patch("app.repositories.projects.get_supabase", return_value=mock_sb):
        from app.repositories.projects import ProjectRepository
        repo = ProjectRepository()
        project = repo.get_by_id("proj-1")
    assert project.id == "proj-1"


def test_project_get_by_id_not_found():
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
    with patch("app.repositories.projects.get_supabase", return_value=mock_sb):
        from app.repositories.projects import ProjectRepository
        repo = ProjectRepository()
        assert repo.get_by_id("missing") is None


def test_video_create():
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value.data = [MOCK_VIDEO_ROW]
    with patch("app.repositories.videos.get_supabase", return_value=mock_sb):
        from app.repositories.videos import VideoRepository
        repo = VideoRepository()
        video = repo.create("proj-1", "user-1", "upload", "video.mp4", r2_key="videos/user-1/proj-1/vid-1/video.mp4")
    assert video.id == "vid-1"
    assert video.source_type == "upload"
    assert video.r2_key == "videos/user-1/proj-1/vid-1/video.mp4"
