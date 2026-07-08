from unittest.mock import MagicMock, patch
from datetime import datetime


def _make_clip_row(**overrides):
    row = {
        "id": "clip-1",
        "project_id": "proj-1",
        "video_id": "vid-1",
        "title": "Momento viral",
        "start_time": 10.0,
        "end_time": 55.0,
        "duration": 45.0,
        "virality_score": 82,
        "virality_reasons": ["Gancho forte", "Alta emoção"],
        "status": "pending",
        "r2_key": None,
        "thumbnail_r2_key": None,
        "resolution": "720p",
        "has_watermark": True,
        "caption_style": "default",
        "created_at": "2026-07-08T00:00:00",
        "updated_at": "2026-07-08T00:00:00",
    }
    row.update(overrides)
    return row


def test_clip_create():
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [_make_clip_row()]
    with patch("app.repositories.clips.get_supabase", return_value=mock_supabase):
        from app.repositories.clips import ClipRepository
        repo = ClipRepository()
        clip = repo.create("proj-1", "vid-1", "Momento viral", 10.0, 55.0, 82, ["Gancho forte"])
    assert clip.id == "clip-1"
    assert clip.virality_score == 82
    assert clip.title == "Momento viral"


def test_clip_get_by_project():
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        _make_clip_row(), _make_clip_row(id="clip-2", virality_score=70)
    ]
    with patch("app.repositories.clips.get_supabase", return_value=mock_supabase):
        from app.repositories.clips import ClipRepository
        repo = ClipRepository()
        clips = repo.get_by_project("proj-1")
    assert len(clips) == 2


def test_clip_get_by_id_not_found():
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = None
    with patch("app.repositories.clips.get_supabase", return_value=mock_supabase):
        from app.repositories.clips import ClipRepository
        repo = ClipRepository()
        result = repo.get_by_id("nonexistent")
    assert result is None
