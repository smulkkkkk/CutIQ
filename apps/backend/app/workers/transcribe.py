import os
import tempfile
import asyncio
from app.repositories.videos import VideoRepository
from app.repositories.jobs import JobRepository
from app.integrations.r2 import download_to_path, upload_from_path
from app.integrations.ffmpeg import extract_audio
from app.integrations.whisper import get_whisper_client
from app.websocket.events import emit_transcribing, emit_transcribed, emit_failed
from app.core.supabase import get_supabase


async def transcribe_video(ctx: dict, *, video_id: str, project_id: str) -> None:
    vid_repo = VideoRepository()
    video = vid_repo.get_by_id(video_id)
    if not video:
        return

    job_repo = JobRepository()
    jobs = job_repo.get_by_project(project_id)
    running_job = next(
        (j for j in jobs if j.type in ("transcribe", "download_youtube") and j.status == "queued"),
        None,
    )
    if running_job:
        job_repo.update(running_job.id, status="running")

    try:
        await emit_transcribing(project_id, 0)

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "video.mp4")
            audio_path = os.path.join(tmpdir, "audio.wav")

            if video.source_type == "youtube" and video.source_url:
                from app.integrations.youtube import download_youtube_to_r2
                await download_youtube_to_r2(video.source_url, video.r2_key)

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, download_to_path, video.r2_key, video_path)
            await emit_transcribing(project_id, 30)

            extract_audio(video_path, audio_path)
            await emit_transcribing(project_id, 60)

            whisper = get_whisper_client()
            result = await asyncio.get_running_loop().run_in_executor(
                None, whisper.transcribe, audio_path
            )
            await emit_transcribing(project_id, 90)

        supabase = get_supabase()
        supabase.table("transcriptions").insert({
            "video_id": video_id,
            "language": result["language"],
            "content": result["text"],
            "segments": result["segments"],
        }).execute()

        vid_repo.update(video_id, status="transcribed")
        if running_job:
            job_repo.update(running_job.id, status="completed", progress=100)

        await emit_transcribed(project_id, video.duration_seconds or 0.0)

    except Exception as e:
        vid_repo.update(video_id, status="failed")
        if running_job:
            job_repo.update(running_job.id, status="failed", error_message=str(e))
        await emit_failed(project_id, str(e))
        raise
