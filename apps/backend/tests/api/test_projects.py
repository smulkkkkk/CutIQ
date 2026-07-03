import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from app.main import app
from app.api.deps import get_current_user

NOW = datetime(2026, 7, 3, tzinfo=timezone.utc)
MOCK_USER = MagicMock(id="user-1", email="test@example.com")
MOCK_PROJECT = MagicMock(
    id="proj-1", user_id="user-1", title="My Video", status="created",
    created_at=NOW, updated_at=NOW,
)


@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_projects(client):
    with patch("app.api.routes.projects.ProjectRepository") as mock_repo_cls:
        mock_repo = MagicMock()
        mock_repo.list_by_user.return_value = [MOCK_PROJECT]
        mock_repo_cls.return_value = mock_repo
        response = await client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "proj-1"


@pytest.mark.asyncio
async def test_create_project(client):
    with patch("app.api.routes.projects.ProjectRepository") as mock_repo_cls:
        mock_repo = MagicMock()
        mock_repo.create.return_value = MOCK_PROJECT
        mock_repo_cls.return_value = mock_repo
        response = await client.post("/api/projects", json={"title": "My Video"})
    assert response.status_code == 201
    assert response.json()["title"] == "My Video"


@pytest.mark.asyncio
async def test_get_project_not_found(client):
    with patch("app.api.routes.projects.ProjectRepository") as mock_repo_cls:
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None
        mock_repo_cls.return_value = mock_repo
        response = await client.get("/api/projects/missing-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_project_wrong_user(client):
    other_project = MagicMock(id="proj-2", user_id="other-user")
    with patch("app.api.routes.projects.ProjectRepository") as mock_repo_cls:
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = other_project
        mock_repo_cls.return_value = mock_repo
        response = await client.get("/api/projects/proj-2")
    assert response.status_code == 404
