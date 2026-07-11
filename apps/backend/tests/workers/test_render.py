import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime


def _make_clip(**overrides):
    from app.models.clip import Clip
    defaults = dict(
        id="clip-1", project_id="proj-1", video_id="vid-1",
        title="Test clip", start_time=10.0, end_time=55.0,
        duration=45.0, virality_score=82,
        virality_reasons=["Gancho"],
        status="pending", r2_key=None, thumbnail_r2_key=None,
        resolution="720p", has_watermark=True, caption_style="default",
        created_at=datetime(2026, 7, 8), updated_at=datetime(2026, 7, 8),
    )
    defaults.update(overrides)
    return Clip(**defaults)


def _make_video(**overrides):
    from app.models.project import Video
    defaults = dict(
        id="vid-1", project_id="proj-1", user_id="user-1",
        source_type="upload", filename="video.mp4",
        status="transcribed", source_url=None, r2_key="videos/vid-1/source.mp4",
        duration_seconds=120.0, size_bytes=None,
        created_at=datetime(2026, 7, 8),
    )
    defaults.update(overrides)
    return Video(**defaults)


@pytest.mark.asyncio
async def test_render_clip_job_success():
    clip = _make_clip()
    video = _make_video()

    mock_clip_repo = MagicMock()
    mock_clip_repo.get_by_id.return_value = clip
    ready_clip = _make_clip(status="ready")
    mock_clip_repo.get_by_project.return_value = [ready_clip]

    mock_video_repo = MagicMock()
    mock_video_repo.get_by_id.return_value = video

    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = {
        "segments": [{"start": 10.0, "end": 20.0, "text": "Hello"}]
    }

    with (
        patch("app.workers.render.ClipRepository", return_value=mock_clip_repo),
        patch("app.workers.render.VideoRepository", return_value=mock_video_repo),
        patch("app.workers.render.get_supabase", return_value=mock_supabase),
        patch("app.workers.render.ProjectRepository") as MockProjRepo,
        patch("app.workers.render.download_to_path"),
        patch("app.workers.render.upload_from_path"),
        patch("app.workers.render.generate_presigned_download_url", return_value="https://example.com/thumb.jpg"),
        patch("app.workers.render.render_clip"),
        patch("app.workers.render.generate_thumbnail"),
        patch("app.workers.render.generate_ass_subtitles", return_value="[Script Info]\n"),
        patch("app.workers.render.emit_rendering", new_callable=AsyncMock),
        patch("app.workers.render.emit_clip_ready", new_callable=AsyncMock) as mock_clip_ready,
        patch("app.workers.render.emit_completed", new_callable=AsyncMock) as mock_completed,
    ):
        from app.workers.render import render_clip_job
        await render_clip_job({}, clip_id="clip-1", project_id="proj-1")

    mock_clip_ready.assert_called_once_with("proj-1", "clip-1", "https://example.com/thumb.jpg")
    mock_completed.assert_called_once_with("proj-1")
    MockProjRepo.return_value.update_status.assert_called_once_with("proj-1", "completed")
    update_calls = mock_clip_repo.update.call_args_list
    assert "ready" in str(update_calls)


@pytest.mark.asyncio
async def test_render_clip_job_missing_clip_returns_early():
    mock_clip_repo = MagicMock()
    mock_clip_repo.get_by_id.return_value = None
    with patch("app.workers.render.ClipRepository", return_value=mock_clip_repo):
        from app.workers.render import render_clip_job
        await render_clip_job({}, clip_id="nonexistent", project_id="proj-1")
    mock_clip_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_render_clip_job_failure_marks_clip_failed():
    clip = _make_clip()
    video = _make_video()

    mock_clip_repo = MagicMock()
    mock_clip_repo.get_by_id.return_value = clip
    failed_clip = _make_clip(status="failed")
    mock_clip_repo.get_by_project.return_value = [failed_clip]

    mock_video_repo = MagicMock()
    mock_video_repo.get_by_id.return_value = video

    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = None

    with (
        patch("app.workers.render.ClipRepository", return_value=mock_clip_repo),
        patch("app.workers.render.VideoRepository", return_value=mock_video_repo),
        patch("app.workers.render.get_supabase", return_value=mock_supabase),
        patch("app.workers.render.ProjectRepository"),
        patch("app.workers.render.download_to_path", side_effect=RuntimeError("storage down")),
        patch("app.workers.render.upload_from_path"),
        patch("app.workers.render.generate_presigned_download_url"),
        patch("app.workers.render.render_clip"),
        patch("app.workers.render.generate_thumbnail"),
        patch("app.workers.render.generate_ass_subtitles", return_value=""),
        patch("app.workers.render.emit_rendering", new_callable=AsyncMock),
        patch("app.workers.render.emit_clip_ready", new_callable=AsyncMock),
        patch("app.workers.render.emit_completed", new_callable=AsyncMock),
        patch("app.workers.render.emit_failed", new_callable=AsyncMock) as mock_failed,
    ):
        from app.workers.render import render_clip_job
        with pytest.raises(RuntimeError):
            await render_clip_job({}, clip_id="clip-1", project_id="proj-1")

    # clip updated to failed
    update_kwargs = {k: v for call in mock_clip_repo.update.call_args_list for k, v in call[1].items()}
    assert update_kwargs.get("status") == "failed"
