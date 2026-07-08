import pytest
from unittest.mock import MagicMock, patch, AsyncMock


@pytest.mark.asyncio
async def test_analyze_video_success():
    mock_transcription = {
        "video_id": "vid-1",
        "language": "pt",
        "content": "hello world",
        "segments": [{"start": 0.0, "end": 5.0, "text": "hello"}],
    }
    mock_clips = [
        {"start_time": 0.0, "end_time": 45.0, "title": "Top Moment", "virality_score": 85, "reasons": ["Gancho forte"]},
    ]
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = mock_transcription

    mock_clip_repo = MagicMock()
    mock_job_repo = MagicMock()
    mock_job = MagicMock()
    mock_job.id = "job-1"
    mock_job.type = "analyze"
    mock_job.status = "queued"
    mock_job_repo.get_by_project.return_value = [mock_job]

    with (
        patch("app.workers.analyze.get_supabase", return_value=mock_supabase),
        patch("app.workers.analyze.ClipRepository", return_value=mock_clip_repo),
        patch("app.workers.analyze.JobRepository", return_value=mock_job_repo),
        patch("app.workers.analyze.ProjectRepository") as MockProjRepo,
        patch("app.workers.analyze.detect_clips", return_value=mock_clips),
        patch("app.workers.analyze.emit_analyzing", new_callable=AsyncMock),
        patch("app.workers.analyze.emit_analyzed", new_callable=AsyncMock) as mock_emit_analyzed,
        patch("app.workers.analyze.emit_completed", new_callable=AsyncMock) as mock_emit_completed,
    ):
        from app.workers.analyze import analyze_video
        await analyze_video({}, video_id="vid-1", project_id="proj-1")

    mock_clip_repo.create.assert_called_once_with(
        project_id="proj-1",
        video_id="vid-1",
        title="Top Moment",
        start_time=0.0,
        end_time=45.0,
        virality_score=85,
        virality_reasons=["Gancho forte"],
    )
    mock_job_repo.update.assert_any_call("job-1", status="completed", progress=100)
    MockProjRepo.return_value.update_status.assert_called_once_with("proj-1", "completed")
    mock_emit_analyzed.assert_called_once_with("proj-1", 1)
    mock_emit_completed.assert_called_once_with("proj-1")


@pytest.mark.asyncio
async def test_analyze_video_no_transcription():
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = None
    with patch("app.workers.analyze.get_supabase", return_value=mock_supabase):
        from app.workers.analyze import analyze_video
        await analyze_video({}, video_id="vid-missing", project_id="proj-1")


@pytest.mark.asyncio
async def test_analyze_video_failure_emits_failed():
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = {
        "video_id": "vid-1", "language": "pt", "content": "hi", "segments": [],
    }
    mock_job_repo = MagicMock()
    mock_job_repo.get_by_project.return_value = []

    with (
        patch("app.workers.analyze.get_supabase", return_value=mock_supabase),
        patch("app.workers.analyze.JobRepository", return_value=mock_job_repo),
        patch("app.workers.analyze.ClipRepository"),
        patch("app.workers.analyze.ProjectRepository"),
        patch("app.workers.analyze.detect_clips", side_effect=RuntimeError("Claude down")),
        patch("app.workers.analyze.emit_analyzing", new_callable=AsyncMock),
        patch("app.workers.analyze.emit_failed", new_callable=AsyncMock) as mock_emit_failed,
    ):
        from app.workers.analyze import analyze_video
        with pytest.raises(RuntimeError):
            await analyze_video({}, video_id="vid-1", project_id="proj-1")

    mock_emit_failed.assert_called_once_with("proj-1", "Claude down")
