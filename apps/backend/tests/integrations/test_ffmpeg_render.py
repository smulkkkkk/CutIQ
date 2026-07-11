from unittest.mock import patch, MagicMock
import pytest


def _run_ok(*args, **kwargs):
    return MagicMock(returncode=0)


def test_render_clip_calls_ffmpeg_with_crop_and_scale():
    with patch("app.integrations.ffmpeg.subprocess.run", side_effect=_run_ok) as mock_run:
        from app.integrations.ffmpeg import render_clip
        render_clip("in.mp4", "out.mp4", 10.0, 55.0, resolution="720p", has_watermark=False)
    args = mock_run.call_args[0][0]
    assert args[0] == "ffmpeg"
    assert "10.0" in args
    assert "55.0" in args
    vf = " ".join(args)
    assert "crop=" in vf
    assert "scale=720:1280" in vf


def test_render_clip_includes_watermark_when_requested():
    with patch("app.integrations.ffmpeg.subprocess.run", side_effect=_run_ok) as mock_run:
        from app.integrations.ffmpeg import render_clip
        render_clip("in.mp4", "out.mp4", 0.0, 30.0, has_watermark=True)
    vf = " ".join(mock_run.call_args[0][0])
    assert "drawtext" in vf


def test_render_clip_includes_captions_when_provided():
    with patch("app.integrations.ffmpeg.subprocess.run", side_effect=_run_ok) as mock_run:
        from app.integrations.ffmpeg import render_clip
        render_clip("in.mp4", "out.mp4", 0.0, 30.0, captions_path="/tmp/subs.ass")
    vf = " ".join(mock_run.call_args[0][0])
    assert "ass=" in vf


def test_render_clip_raises_on_ffmpeg_failure():
    import subprocess
    with patch(
        "app.integrations.ffmpeg.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "ffmpeg", stderr=b"encoding error"),
    ):
        from app.integrations.ffmpeg import render_clip
        with pytest.raises(RuntimeError, match="FFmpeg render failed"):
            render_clip("in.mp4", "out.mp4", 0.0, 30.0)


def test_generate_thumbnail_calls_ffmpeg():
    with patch("app.integrations.ffmpeg.subprocess.run", side_effect=_run_ok) as mock_run:
        from app.integrations.ffmpeg import generate_thumbnail
        generate_thumbnail("clip.mp4", "thumb.jpg", at_second=2.5)
    args = mock_run.call_args[0][0]
    assert "ffmpeg" == args[0]
    assert "2.5" in " ".join(str(a) for a in args)
    assert "thumb.jpg" in args


def test_generate_thumbnail_raises_on_failure():
    import subprocess
    with patch(
        "app.integrations.ffmpeg.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "ffmpeg", stderr=b"bad"),
    ):
        from app.integrations.ffmpeg import generate_thumbnail
        with pytest.raises(RuntimeError, match="FFmpeg thumbnail failed"):
            generate_thumbnail("clip.mp4", "thumb.jpg")


def test_render_clip_unknown_resolution_falls_back_to_720p():
    with patch("app.integrations.ffmpeg.subprocess.run", side_effect=_run_ok) as mock_run:
        from app.integrations.ffmpeg import render_clip
        render_clip("in.mp4", "out.mp4", 0.0, 30.0, resolution="unknown_res", has_watermark=False)
    vf = " ".join(mock_run.call_args[0][0])
    assert "scale=720:1280" in vf
