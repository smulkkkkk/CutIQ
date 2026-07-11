import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.main import app
from app.api.deps import get_current_user
from app.models.clip import Clip
from app.models.project import Project

MOCK_USER = MagicMock(id="user-1", email="test@example.com")
MOCK_CLIP = Clip(
    id="clip-1", project_id="proj-1", video_id="vid-1",
    title="Momento viral", start_time=10.0, end_time=55.0,
    duration=45.0, virality_score=82,
    virality_reasons=["Gancho forte"],
    status="pending", r2_key=None, thumbnail_r2_key=None,
    resolution="720p", has_watermark=True, caption_style="default",
    created_at=datetime(2026, 7, 8), updated_at=datetime(2026, 7, 8),
)
MOCK_PROJECT = Project(
    id="proj-1",
    user_id="user-1",
    title="Test Project",
    status="created",
    created_at=datetime(2026, 7, 8),
    updated_at=datetime(2026, 7, 8),
)


@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_clips_returns_200(client):
    with patch("app.api.routes.clips.ProjectRepository") as mock_proj_cls, \
         patch("app.api.routes.clips.ClipRepository") as mock_repo_cls:
        mock_proj = MagicMock()
        mock_proj.get_by_id.return_value = MOCK_PROJECT
        mock_proj_cls.return_value = mock_proj

        mock_repo = MagicMock()
        mock_repo.get_by_project.return_value = [MOCK_CLIP]
        mock_repo_cls.return_value = mock_repo

        response = await client.get("/api/clips?project_id=proj-1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "clip-1"
    assert data[0]["virality_score"] == 82


@pytest.mark.asyncio
async def test_list_clips_missing_project_id(client):
    response = await client.get("/api/clips")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_clips_foreign_project_returns_404(client):
    with patch("app.api.routes.clips.ProjectRepository") as mock_proj_cls:
        mock_proj = MagicMock()
        mock_proj.get_by_id.return_value = None
        mock_proj_cls.return_value = mock_proj

        response = await client.get("/api/clips?project_id=foreign-proj")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_clips_wrong_owner_returns_404(client):
    foreign_project = Project(
        id="foreign-proj",
        user_id="other-user",
        title="Someone else's project",
        status="created",
        created_at=datetime(2026, 7, 8),
        updated_at=datetime(2026, 7, 8),
    )
    with patch("app.api.routes.clips.ProjectRepository") as mock_proj_cls:
        mock_proj = MagicMock()
        mock_proj.get_by_id.return_value = foreign_project
        mock_proj_cls.return_value = mock_proj

        response = await client.get("/api/clips?project_id=foreign-proj")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_clip_returns_url(client):
    mock_clip = Clip(
        id="clip-1", project_id="proj-1", video_id="vid-1",
        title="Test", start_time=0.0, end_time=45.0, duration=45.0,
        virality_score=80, virality_reasons=[], status="ready",
        r2_key="clips/clip-1/clip.mp4", thumbnail_r2_key=None,
        resolution="720p", has_watermark=True, caption_style="default",
        created_at=datetime(2026, 7, 8), updated_at=datetime(2026, 7, 8),
    )
    mock_project = MagicMock()
    mock_project.user_id = "user-1"

    mock_clip_repo = MagicMock()
    mock_clip_repo.get_by_id.return_value = mock_clip

    with (
        patch("app.api.routes.clips.ClipRepository", return_value=mock_clip_repo),
        patch("app.api.routes.clips.ProjectRepository") as MockProjRepo,
        patch("app.api.routes.clips.generate_presigned_download_url", return_value="https://storage/clip.mp4"),
    ):
        MockProjRepo.return_value.get_by_id.return_value = mock_project
        response = await client.get("/api/clips/clip-1/download")
    assert response.status_code == 200
    data = response.json()
    assert "download_url" in data
    assert data["download_url"] == "https://storage/clip.mp4"
    assert "filename" in data
    assert data["filename"] == "Test.mp4"


@pytest.mark.asyncio
async def test_download_clip_not_found_returns_404(client):
    mock_clip_repo = MagicMock()
    mock_clip_repo.get_by_id.return_value = None
    with patch("app.api.routes.clips.ClipRepository", return_value=mock_clip_repo):
        response = await client.get("/api/clips/nonexistent/download")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_clip_not_ready_returns_404(client):
    mock_clip = Clip(
        id="clip-1", project_id="proj-1", video_id="vid-1",
        title="Test", start_time=0.0, end_time=45.0, duration=45.0,
        virality_score=80, virality_reasons=[], status="pending",
        r2_key=None, thumbnail_r2_key=None,
        resolution="720p", has_watermark=True, caption_style="default",
        created_at=datetime(2026, 7, 8), updated_at=datetime(2026, 7, 8),
    )
    mock_project = MagicMock()
    mock_project.user_id = "user-1"
    mock_clip_repo = MagicMock()
    mock_clip_repo.get_by_id.return_value = mock_clip
    with (
        patch("app.api.routes.clips.ClipRepository", return_value=mock_clip_repo),
        patch("app.api.routes.clips.ProjectRepository") as MockProjRepo,
    ):
        MockProjRepo.return_value.get_by_id.return_value = mock_project
        response = await client.get("/api/clips/clip-1/download")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_clip_wrong_owner_returns_404(client):
    mock_clip = Clip(
        id="clip-1", project_id="proj-1", video_id="vid-1",
        title="Test", start_time=0.0, end_time=45.0, duration=45.0,
        virality_score=80, virality_reasons=[], status="ready",
        r2_key="clips/clip-1/clip.mp4", thumbnail_r2_key=None,
        resolution="720p", has_watermark=True, caption_style="default",
        created_at=datetime(2026, 7, 8), updated_at=datetime(2026, 7, 8),
    )
    mock_project = MagicMock()
    mock_project.user_id = "other-user"
    mock_clip_repo = MagicMock()
    mock_clip_repo.get_by_id.return_value = mock_clip
    with (
        patch("app.api.routes.clips.ClipRepository", return_value=mock_clip_repo),
        patch("app.api.routes.clips.ProjectRepository") as MockProjRepo,
    ):
        MockProjRepo.return_value.get_by_id.return_value = mock_project
        response = await client.get("/api/clips/clip-1/download")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_clip_project_not_found_returns_404(client):
    mock_clip = Clip(
        id="clip-1", project_id="proj-1", video_id="vid-1",
        title="Test", start_time=0.0, end_time=45.0, duration=45.0,
        virality_score=80, virality_reasons=[], status="ready",
        r2_key="clips/clip-1/clip.mp4", thumbnail_r2_key=None,
        resolution="720p", has_watermark=True, caption_style="default",
        created_at=datetime(2026, 7, 8), updated_at=datetime(2026, 7, 8),
    )
    mock_clip_repo = MagicMock()
    mock_clip_repo.get_by_id.return_value = mock_clip
    with (
        patch("app.api.routes.clips.ClipRepository", return_value=mock_clip_repo),
        patch("app.api.routes.clips.ProjectRepository") as MockProjRepo,
    ):
        MockProjRepo.return_value.get_by_id.return_value = None
        response = await client.get("/api/clips/clip-1/download")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_clip_filename_replaces_spaces(client):
    mock_clip = Clip(
        id="clip-1", project_id="proj-1", video_id="vid-1",
        title="My Test Clip", start_time=0.0, end_time=45.0, duration=45.0,
        virality_score=80, virality_reasons=[], status="ready",
        r2_key="clips/clip-1/clip.mp4", thumbnail_r2_key=None,
        resolution="720p", has_watermark=True, caption_style="default",
        created_at=datetime(2026, 7, 8), updated_at=datetime(2026, 7, 8),
    )
    mock_project = MagicMock()
    mock_project.user_id = "user-1"
    mock_clip_repo = MagicMock()
    mock_clip_repo.get_by_id.return_value = mock_clip
    with (
        patch("app.api.routes.clips.ClipRepository", return_value=mock_clip_repo),
        patch("app.api.routes.clips.ProjectRepository") as MockProjRepo,
        patch("app.api.routes.clips.generate_presigned_download_url", return_value="https://storage/clip.mp4"),
    ):
        MockProjRepo.return_value.get_by_id.return_value = mock_project
        response = await client.get("/api/clips/clip-1/download")
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "My_Test_Clip.mp4"
