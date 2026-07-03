import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

@pytest.fixture
def mock_supabase_user():
    user = MagicMock()
    user.id = "test-user-id"
    user.email = "test@example.com"
    return user
