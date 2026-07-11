import pytest
from unittest.mock import MagicMock, patch, AsyncMock


def _make_mock_supabase(with_transcription=True):
    mock_supabase = MagicMock()
    if with_transcription:
        mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = {
            "video_id": "vid-1",
            "language": "pt",
            "content": "hello world",
            "segments": [{"start": 0.0, "end": 5.0, "text": "hello"}],
        }
    else:
        mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = None
    return mock_supabase


@pytest.mark.asyncio
async def test_analyze_video_success():
    mock_clips_data = [
        {"start_time": 0.0, "end_time": 45.0, "title": "Top Moment", "virality_score": 85, "reasons": ["Gancho forte"]},
        {"start_time": 50.0, "end_time": 90.0, "title": "Second", "virality_score": 70, "reasons": ["Emoção"]},
    ]
    mock_clip_repo = MagicMock()
    mock_saved_clip_1 = MagicMock(); mock_saved_clip_1.id = "clip-1"
    mock_saved_clip_2 = MagicMock(); mock_saved_clip_2.id = "clip-2"
    mock_clip_repo.create.side_effect = [mock_saved_clip_1, mock_saved_clip_2]

    mock_job_repo = MagicMock()
    mock_job = MagicMock(); mock_job.id = "job-1"; mock_job.type = "analyze"; mock_job.status = "queued"
    mock_job_repo.get_by_project.return_value = [mock_job]

    mock_enqueue = AsyncMock(return_value="arq-id-1")

    with (
        patch("app.workers.analyze.get_supabase", return_value=_make_mock_supabase()),
        patch("app.workers.analyze.ClipRepository", return_value=mock_clip_repo),
        patch("app.workers.analyze.JobRepository", return_value=mock_job_repo),
        patch("app.workers.analyze.ProjectRepository") as MockProjRepo,
        patch("app.workers.analyze.detect_clips", return_value=mock_clips_data),
        patch("app.workers.analyze.emit_analyzing", new_callable=AsyncMock),
        patch("app.workers.analyze.emit_analyzed", new_callable=AsyncMock) as mock_emit_analyzed,
        patch("app.workers.analyze.enqueue_job", mock_enqueue),
    ):
        from app.workers.analyze import analyze_video
        await analyze_video({}, video_id="vid-1", project_id="proj-1")

    assert mock_clip_repo.create.call_count == 2
    assert mock_enqueue.call_count == 2
    mock_enqueue.assert_any_call("render_clip_job", clip_id="clip-1", project_id="proj-1")
    mock_enqueue.assert_any_call("render_clip_job", clip_id="clip-2", project_id="proj-1")
    MockProjRepo.return_value.update_status.assert_called_once_with("proj-1", "rendering")
    mock_emit_analyzed.assert_called_once_with("proj-1", 2)


@pytest.mark.asyncio
async def test_analyze_video_no_transcription():
    with patch("app.workers.analyze.get_supabase", return_value=_make_mock_supabase(with_transcription=False)):
        from app.workers.analyze import analyze_video
        await analyze_video({}, video_id="vid-missing", project_id="proj-1")


@pytest.mark.asyncio
async def test_analyze_video_failure_emits_failed():
    mock_job_repo = MagicMock()
    mock_job_repo.get_by_project.return_value = []

    with (
        patch("app.workers.analyze.get_supabase", return_value=_make_mock_supabase()),
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
