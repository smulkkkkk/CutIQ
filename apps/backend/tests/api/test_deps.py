import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from app.api.deps import get_current_user

# App temporário para testar o dep isolado
_test_app = FastAPI()

@_test_app.get("/protected")
async def protected_route(user=__import__('fastapi').Depends(get_current_user)):
    return {"user_id": user.id}

@pytest.fixture
async def dep_client():
    async with AsyncClient(
        transport=ASGITransport(app=_test_app), base_url="http://test"
    ) as ac:
        yield ac

@pytest.mark.asyncio
async def test_no_token_returns_403(dep_client):
    response = await dep_client.get("/protected")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_invalid_token_returns_401(dep_client):
    with patch("app.api.deps.get_supabase") as mock_get:
        from supabase import AuthApiError
        mock_sb = MagicMock()
        mock_sb.auth.get_user.side_effect = AuthApiError("invalid", 401, {})
        mock_get.return_value = mock_sb

        response = await dep_client.get(
            "/protected", headers={"Authorization": "Bearer bad-token"}
        )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_valid_token_returns_user(dep_client, mock_supabase_user):
    with patch("app.api.deps.get_supabase") as mock_get:
        mock_sb = MagicMock()
        mock_sb.auth.get_user.return_value = MagicMock(user=mock_supabase_user)
        mock_get.return_value = mock_sb

        response = await dep_client.get(
            "/protected", headers={"Authorization": "Bearer valid-token"}
        )
    assert response.status_code == 200
    assert response.json()["user_id"] == "test-user-id"
