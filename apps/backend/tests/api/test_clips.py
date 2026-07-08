import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.main import app
from app.api.deps import get_current_user
from app.models.clip import Clip

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


@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_clips_returns_200(client):
    with patch("app.api.routes.clips.ClipRepository") as mock_repo_cls:
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
