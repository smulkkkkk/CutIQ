import subprocess


def extract_audio(video_path: str, output_path: str) -> None:
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-ar", "16000",
        "-ac", "1",
        "-f", "wav",
        output_path,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else ""
        raise RuntimeError(f"FFmpeg audio extraction failed: {stderr}")
