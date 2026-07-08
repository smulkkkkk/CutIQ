import asyncio
from app.repositories.clips import ClipRepository
from app.repositories.jobs import JobRepository
from app.repositories.projects import ProjectRepository
from app.integrations.claude import detect_clips
from app.websocket.events import emit_analyzing, emit_analyzed, emit_completed, emit_failed
from app.core.supabase import get_supabase


async def analyze_video(ctx: dict, *, video_id: str, project_id: str) -> None:
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
            clip_repo.create(
                project_id=project_id,
                video_id=video_id,
                title=clip["title"],
                start_time=clip["start_time"],
                end_time=clip["end_time"],
                virality_score=clip["virality_score"],
                virality_reasons=clip["reasons"],
            )

        if running_job:
            job_repo.update(running_job.id, status="completed", progress=100)

        ProjectRepository().update_status(project_id, "completed")
        await emit_analyzed(project_id, len(clips_data))
        await emit_completed(project_id)

    except Exception as e:
        if running_job:
            job_repo.update(running_job.id, status="failed", error_message=str(e))
        await emit_failed(project_id, str(e))
        raise
