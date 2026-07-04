import pytest
from unittest.mock import MagicMock, patch, AsyncMock


MOCK_VIDEO_UPLOAD = MagicMock(
    id="vid-1",
    project_id="proj-1",
    user_id="user-1",
    source_type="upload",
    source_url=None,
    r2_key="videos/user-1/proj-1/vid-1/video.mp4",
    status="processing",
    duration_seconds=120.0,
)

MOCK_VIDEO_YOUTUBE = MagicMock(
    id="vid-2",
    project_id="proj-1",
    user_id="user-1",
    source_type="youtube",
    source_url="https://www.youtube.com/watch?v=test",
    r2_key="videos/vid-2/source.mp4",
    status="processing",
    duration_seconds=60.0,
)

MOCK_TRANSCRIPTION_RESULT = {
    "language": "en",
    "segments": [{"start": 0.0, "end": 5.0, "text": " Hello world"}],
    "text": " Hello world",
}


@pytest.mark.asyncio
async def test_transcribe_video_success_upload():
    mock_vid_repo = MagicMock()
    mock_vid_repo.get_by_id.return_value = MOCK_VIDEO_UPLOAD

    mock_job_repo = MagicMock()
    mock_job_repo.get_by_project.return_value = []

    mock_whisper = MagicMock()
    mock_whisper.transcribe.return_value = MOCK_TRANSCRIPTION_RESULT

    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value = MagicMock()

    with patch("app.workers.transcribe.VideoRepository", return_value=mock_vid_repo), \
         patch("app.workers.transcribe.JobRepository", return_value=mock_job_repo), \
         patch("app.workers.transcribe.get_whisper_client", return_value=mock_whisper), \
         patch("app.workers.transcribe.download_to_path"), \
         patch("app.workers.transcribe.upload_from_path"), \
         patch("app.workers.transcribe.extract_audio"), \
         patch("app.workers.transcribe.emit_transcribing", new_callable=AsyncMock), \
         patch("app.workers.transcribe.emit_transcribed", new_callable=AsyncMock), \
         patch("app.workers.transcribe.get_supabase", return_value=mock_sb), \
         patch("tempfile.TemporaryDirectory") as mock_tmpdir:
        mock_tmpdir.return_value.__enter__.return_value = "/tmp/fakedir"
        mock_tmpdir.return_value.__exit__.return_value = False

        from app.workers.transcribe import transcribe_video
        await transcribe_video({}, video_id="vid-1", project_id="proj-1")

    mock_vid_repo.update.assert_called_with("vid-1", status="transcribed")
    mock_sb.table.assert_called_with("transcriptions")


@pytest.mark.asyncio
async def test_transcribe_video_success_youtube():
    mock_vid_repo = MagicMock()
    mock_vid_repo.get_by_id.return_value = MOCK_VIDEO_YOUTUBE

    mock_job_repo = MagicMock()
    mock_job_repo.get_by_project.return_value = []

    mock_whisper = MagicMock()
    mock_whisper.transcribe.return_value = MOCK_TRANSCRIPTION_RESULT

    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value = MagicMock()

    mock_dl_yt = AsyncMock(return_value={"r2_key": "videos/vid-2/source.mp4", "title": "Test", "duration": 60})

    with patch("app.workers.transcribe.VideoRepository", return_value=mock_vid_repo), \
         patch("app.workers.transcribe.JobRepository", return_value=mock_job_repo), \
         patch("app.workers.transcribe.get_whisper_client", return_value=mock_whisper), \
         patch("app.workers.transcribe.download_to_path"), \
         patch("app.workers.transcribe.upload_from_path"), \
         patch("app.workers.transcribe.extract_audio"), \
         patch("app.workers.transcribe.emit_transcribing", new_callable=AsyncMock), \
         patch("app.workers.transcribe.emit_transcribed", new_callable=AsyncMock), \
         patch("app.workers.transcribe.get_supabase", return_value=mock_sb), \
         patch("app.integrations.youtube.download_youtube_to_r2", mock_dl_yt), \
         patch("tempfile.TemporaryDirectory") as mock_tmpdir:
        mock_tmpdir.return_value.__enter__.return_value = "/tmp/fakedir"
        mock_tmpdir.return_value.__exit__.return_value = False

        from app.workers.transcribe import transcribe_video
        await transcribe_video({}, video_id="vid-2", project_id="proj-1")

    mock_vid_repo.update.assert_called_with("vid-2", status="transcribed")


@pytest.mark.asyncio
async def test_transcribe_video_not_found():
    mock_vid_repo = MagicMock()
    mock_vid_repo.get_by_id.return_value = None

    with patch("app.workers.transcribe.VideoRepository", return_value=mock_vid_repo):
        from app.workers.transcribe import transcribe_video
        # Should return silently without raising
        await transcribe_video({}, video_id="missing", project_id="proj-1")

    mock_vid_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_transcribe_video_failure_updates_status():
    mock_vid_repo = MagicMock()
    mock_vid_repo.get_by_id.return_value = MOCK_VIDEO_UPLOAD

    mock_job_repo = MagicMock()
    mock_job_repo.get_by_project.return_value = []

    with patch("app.workers.transcribe.VideoRepository", return_value=mock_vid_repo), \
         patch("app.workers.transcribe.JobRepository", return_value=mock_job_repo), \
         patch("app.workers.transcribe.emit_transcribing", new_callable=AsyncMock), \
         patch("app.workers.transcribe.emit_failed", new_callable=AsyncMock) as mock_emit_failed, \
         patch("app.workers.transcribe.download_to_path", side_effect=RuntimeError("R2 error")), \
         patch("tempfile.TemporaryDirectory") as mock_tmpdir:
        mock_tmpdir.return_value.__enter__.return_value = "/tmp/fakedir"
        mock_tmpdir.return_value.__exit__.return_value = False

        from app.workers.transcribe import transcribe_video
        with pytest.raises(RuntimeError, match="R2 error"):
            await transcribe_video({}, video_id="vid-1", project_id="proj-1")

    mock_vid_repo.update.assert_called_with("vid-1", status="failed")
    mock_emit_failed.assert_called_once_with("proj-1", "R2 error")
