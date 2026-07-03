import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

MOCK_PROFILE = MagicMock(
    id="test-user-id",
    full_name="Test User",
    avatar_url=None,
    plan="free",
    credits_used=0,
    credits_limit=3,
    is_admin=False,
    created_at=datetime(2026, 7, 2, tzinfo=timezone.utc),
    updated_at=datetime(2026, 7, 2, tzinfo=timezone.utc),
)

@pytest.mark.asyncio
async def test_get_me_without_token(client):
    response = await client.get("/api/auth/me")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_me_with_invalid_token(client):
    with patch("app.api.deps.get_supabase") as mock_get:
        from supabase import AuthApiError
        mock_sb = MagicMock()
        mock_sb.auth.get_user.side_effect = AuthApiError("invalid", 401, {})
        mock_get.return_value = mock_sb

        response = await client.get(
            "/api/auth/me", headers={"Authorization": "Bearer bad"}
        )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_me_returns_profile(client, mock_supabase_user):
    with patch("app.api.deps.get_supabase") as mock_deps_sb, \
         patch("app.api.routes.auth.UserRepository") as mock_repo_cls:

        mock_sb = MagicMock()
        mock_sb.auth.get_user.return_value = MagicMock(user=mock_supabase_user)
        mock_deps_sb.return_value = mock_sb

        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = MOCK_PROFILE
        mock_repo_cls.return_value = mock_repo

        response = await client.get(
            "/api/auth/me", headers={"Authorization": "Bearer valid"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-user-id"
    assert data["plan"] == "free"
    assert data["credits_limit"] == 3

@pytest.mark.asyncio
async def test_get_me_profile_not_found(client, mock_supabase_user):
    with patch("app.api.deps.get_supabase") as mock_deps_sb, \
         patch("app.api.routes.auth.UserRepository") as mock_repo_cls:

        mock_sb = MagicMock()
        mock_sb.auth.get_user.return_value = MagicMock(user=mock_supabase_user)
        mock_deps_sb.return_value = mock_sb

        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None
        mock_repo_cls.return_value = mock_repo

        response = await client.get(
            "/api/auth/me", headers={"Authorization": "Bearer valid"}
        )

    assert response.status_code == 404
