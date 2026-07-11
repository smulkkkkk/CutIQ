import asyncio
import os
import tempfile
from pathlib import Path

from app.repositories.clips import ClipRepository
from app.repositories.videos import VideoRepository
from app.repositories.projects import ProjectRepository
from app.integrations.ffmpeg import render_clip, generate_thumbnail
from app.integrations.captions import generate_ass_subtitles
from app.integrations.r2 import download_to_path, upload_from_path, generate_presigned_download_url
from app.websocket.events import emit_rendering, emit_clip_ready, emit_completed, emit_failed
from app.core.supabase import get_supabase


async def render_clip_job(_ctx: dict, *, clip_id: str, project_id: str) -> None:
    clip_repo = ClipRepository()
    clip = clip_repo.get_by_id(clip_id)
    if not clip:
        return

    video_repo = VideoRepository()
    video = video_repo.get_by_id(clip.video_id)
    if not video or not video.r2_key:
        return

    try:
        clip_repo.update(clip_id, status="rendering")
        await emit_rendering(project_id, clip_id, 0)

        supabase = get_supabase()
        trans = (
            supabase.table("transcriptions")
            .select("segments")
            .eq("video_id", clip.video_id)
            .maybe_single()
            .execute()
        )

        loop = asyncio.get_running_loop()

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "source.mp4")
            output_path = os.path.join(tmpdir, "clip.mp4")
            thumb_path = os.path.join(tmpdir, "thumb.jpg")
            ass_path = os.path.join(tmpdir, "captions.ass")

            await loop.run_in_executor(None, download_to_path, video.r2_key, video_path)
            await emit_rendering(project_id, clip_id, 20)

            captions_file: str | None = None
            if trans.data and trans.data.get("segments"):
                ass_content = generate_ass_subtitles(
                    trans.data["segments"], clip.start_time, clip.end_time
                )
                Path(ass_path).write_text(ass_content, encoding="utf-8")
                captions_file = ass_path

            await emit_rendering(project_id, clip_id, 40)

            await loop.run_in_executor(
                None,
                render_clip,
                video_path,
                output_path,
                clip.start_time,
                clip.end_time,
                clip.resolution,
                clip.has_watermark,
                captions_file,
            )

            await emit_rendering(project_id, clip_id, 70)

            await loop.run_in_executor(None, generate_thumbnail, output_path, thumb_path, 1.0)

            await emit_rendering(project_id, clip_id, 85)

            r2_key = f"clips/{clip_id}/clip.mp4"
            thumb_key = f"clips/{clip_id}/thumb.jpg"
            await loop.run_in_executor(None, upload_from_path, output_path, r2_key, "video/mp4")
            await loop.run_in_executor(None, upload_from_path, thumb_path, thumb_key, "image/jpeg")

        thumbnail_url = generate_presigned_download_url(thumb_key, expires_in=86400)
        clip_repo.update(clip_id, status="ready", r2_key=r2_key, thumbnail_r2_key=thumb_key)
        await emit_rendering(project_id, clip_id, 100)

        all_clips = clip_repo.get_by_project(project_id)
        if all(c.status in ("ready", "failed") for c in all_clips):
            ProjectRepository().update_status(project_id, "completed")
            await emit_completed(project_id)

        await emit_clip_ready(project_id, clip_id, thumbnail_url)

    except Exception as e:
        clip_repo.update(clip_id, status="failed")
        all_clips = clip_repo.get_by_project(project_id)
        if all(c.status in ("ready", "failed") for c in all_clips):
            ProjectRepository().update_status(project_id, "completed")
            await emit_completed(project_id)
        await emit_failed(project_id, str(e))
        raise
