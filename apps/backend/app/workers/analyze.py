import asyncio
from app.repositories.clips import ClipRepository
from app.repositories.jobs import JobRepository
from app.repositories.projects import ProjectRepository
from app.integrations.claude import detect_clips
from app.websocket.events import emit_analyzing, emit_analyzed, emit_failed
from app.core.supabase import get_supabase


async def enqueue_job(function_name: str, **kwargs) -> str:  # pragma: no cover
    """Thin shim – defers import of queue.py to avoid circular dependency at module load time.

    Tests patch ``app.workers.analyze.enqueue_job`` to replace this function
    with a mock without triggering the circular import.
    """
    from app.workers.queue import enqueue_job as _real_enqueue_job
    return await _real_enqueue_job(function_name, **kwargs)


async def analyze_video(_ctx: dict, *, video_id: str, project_id: str) -> None:
    supabase = get_supabase()
    result = (
        supabase.table("transcriptions")
        .select("*")
        .eq("video_id", video_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        return

    transcription = result.data
    job_repo = JobRepository()
    jobs = job_repo.get_by_project(project_id)
    running_job = next(
        (j for j in jobs if j.type == "analyze" and j.status == "queued"), None
    )
    if running_job:
        job_repo.update(running_job.id, status="running")

    try:
        await emit_analyzing(project_id, 0)

        loop = asyncio.get_running_loop()
        clips_data = await loop.run_in_executor(
            None,
            detect_clips,
            transcription.get("segments") or [],
            transcription.get("content") or "",
        )

        await emit_analyzing(project_id, 80)

        clip_repo = ClipRepository()
        for clip in clips_data:
            saved = clip_repo.create(
                project_id=project_id,
                video_id=video_id,
                title=clip["title"],
                start_time=clip["start_time"],
                end_time=clip["end_time"],
                virality_score=clip["virality_score"],
                virality_reasons=clip["reasons"],
            )
            arq_job_id = await enqueue_job("render_clip_job", clip_id=saved.id, project_id=project_id)
            job_repo.create(project_id, "render", arq_job_id=arq_job_id)

        if running_job:
            job_repo.update(running_job.id, status="completed", progress=100)

        ProjectRepository().update_status(project_id, "rendering")
        await emit_analyzed(project_id, len(clips_data))

    except Exception as e:
        if running_job:
            job_repo.update(running_job.id, status="failed", error_message=str(e))
        await emit_failed(project_id, str(e))
        raise
