import subprocess

_RESOLUTION: dict[str, tuple[int, int]] = {
    "720p": (720, 1280),
    "1080p": (1080, 1920),
    "4k": (2160, 3840),
}


def extract_audio(video_path: str, audio_path: str) -> None:
    cmd = ["ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path, "-y"]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else ""
        raise RuntimeError(f"FFmpeg audio extraction failed: {stderr}")


def render_clip(
    input_path: str,
    output_path: str,
    start_time: float,
    end_time: float,
    resolution: str = "720p",
    has_watermark: bool = True,
    captions_path: str | None = None,
) -> None:
    w, h = _RESOLUTION.get(resolution, (720, 1280))

    vf_parts = [
        "crop=min(iw,ih*9/16):min(ih,iw*16/9):(iw-min(iw,ih*9/16))/2:(ih-min(ih,iw*16/9))/2",
        f"scale={w}:{h}",
    ]

    if captions_path:
        # FFmpeg ass filter requires forward slashes; colon in drive letter must be escaped
        norm = captions_path.replace("\\", "/").replace(":", "\\:")
        vf_parts.append(f"ass='{norm}'")

    if has_watermark:
        vf_parts.append(
            "drawtext=text='CutIQ':fontcolor=white@0.8:fontsize=24:x=w-tw-20:y=h-th-20"
        )

    cmd = [
        "ffmpeg",
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", input_path,
        "-vf", ",".join(vf_parts),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        "-y", output_path,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else ""
        raise RuntimeError(f"FFmpeg render failed: {stderr[:500]}")


def generate_thumbnail(video_path: str, output_path: str, at_second: float = 0.0) -> None:
    cmd = [
        "ffmpeg",
        "-ss", str(at_second),
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        output_path,
        "-y",
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else ""
        raise RuntimeError(f"FFmpeg thumbnail failed: {stderr[:500]}")
