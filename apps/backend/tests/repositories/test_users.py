import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

MOCK_PROFILE_DATA = {
    "id": "test-user-id",
    "full_name": "Test User",
    "avatar_url": None,
    "plan": "free",
    "credits_used": 0,
    "credits_limit": 3,
    "is_admin": False,
    "stripe_customer_id": None,
    "created_at": "2026-07-02T00:00:00+00:00",
    "updated_at": "2026-07-02T00:00:00+00:00",
}

@pytest.fixture
def repo_with_mock():
    with patch("app.repositories.base.get_supabase") as mock_get:
        mock_sb = MagicMock()
        mock_get.return_value = mock_sb
        from app.repositories.users import UserRepository
        repo = UserRepository()
        repo.client = mock_sb
        yield repo, mock_sb

def test_get_by_id_returns_profile(repo_with_mock):
    repo, mock_sb = repo_with_mock
    mock_sb.table().select().eq().single().execute.return_value = MagicMock(
        data=MOCK_PROFILE_DATA
    )
    profile = repo.get_by_id("test-user-id")
    assert profile is not None
    assert profile.id == "test-user-id"
    assert profile.plan == "free"
    assert profile.credits_limit == 3

def test_get_by_id_returns_none_when_not_found(repo_with_mock):
    repo, mock_sb = repo_with_mock
    mock_sb.table().select().eq().single().execute.return_value = MagicMock(data=None)
    profile = repo.get_by_id("nonexistent")
    assert profile is None
