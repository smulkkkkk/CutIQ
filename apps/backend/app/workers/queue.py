from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings
from app.workers.transcribe import transcribe_video


async def get_redis_pool():
    return await create_pool(RedisSettings.from_dsn(settings.redis_url))


async def enqueue_job(function_name: str, **kwargs) -> str:
    """Enqueue a job and return the job_id."""
    pool = await get_redis_pool()
    job = await pool.enqueue_job(function_name, **kwargs)
    return job.job_id


async def startup(ctx: dict) -> None:
    pass


async def shutdown(ctx: dict) -> None:
    pass


class WorkerSettings:
    functions = [transcribe_video]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10
    job_timeout = 3600  # 1 hour per job
    keep_result = 86400  # keep job results for 24h
