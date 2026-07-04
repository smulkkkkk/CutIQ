import asyncio
import os
import tempfile
import yt_dlp
from app.integrations.r2 import upload_from_path


async def get_youtube_info(url: str) -> dict:
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        return {
            "title": info.get("title", ""),
            "duration": int(info.get("duration", 0)),
            "thumbnail_url": info.get("thumbnail", ""),
            "uploader": info.get("uploader", ""),
        }


async def download_youtube_to_r2(url: str, r2_key: str) -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")
        ydl_opts = {
            "outtmpl": output_template,
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            ydl.prepare_filename(info)

        files = os.listdir(tmpdir)
        video_file = os.path.join(tmpdir, files[0])
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, upload_from_path, video_file, r2_key, "video/mp4")

        return {
            "r2_key": r2_key,
            "title": info.get("title", ""),
            "duration": int(info.get("duration", 0)),
        }
