import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.workers.queue import enqueue_job, WorkerSettings


@pytest.mark.asyncio
async def test_enqueue_job_returns_job_id():
    with patch("app.workers.queue.get_redis_pool") as mock_pool_fn:
        mock_pool = AsyncMock()
        mock_job = MagicMock()
        mock_job.job_id = "test-job-id"
        mock_pool.enqueue_job = AsyncMock(return_value=mock_job)
        mock_pool_fn.return_value = mock_pool

        result = await enqueue_job("transcribe_video", video_id="v1", project_id="p1")
        assert result == "test-job-id"
        mock_pool.enqueue_job.assert_called_once_with(
            "transcribe_video", video_id="v1", project_id="p1"
        )


def test_worker_settings_structure():
    assert hasattr(WorkerSettings, "functions")
    assert isinstance(WorkerSettings.functions, list)
    assert hasattr(WorkerSettings, "redis_settings")
    assert WorkerSettings.redis_settings is not None
    assert hasattr(WorkerSettings, "max_jobs")
    assert WorkerSettings.max_jobs == 10
    assert hasattr(WorkerSettings, "job_timeout")
    assert WorkerSettings.job_timeout == 3600
    assert hasattr(WorkerSettings, "keep_result")
    assert WorkerSettings.keep_result == 86400
