from app.websocket.manager import ws_manager


async def emit_transcribing(project_id: str, progress: int) -> None:
    await ws_manager.send_to_project(project_id, {"stage": "transcribing", "progress": progress})


async def emit_transcribed(project_id: str, duration: float) -> None:
    await ws_manager.send_to_project(project_id, {"stage": "transcribed", "duration": duration})


async def emit_analyzing(project_id: str, progress: int) -> None:
    await ws_manager.send_to_project(project_id, {"stage": "analyzing", "progress": progress})


async def emit_rendering(project_id: str, clip_id: str, progress: int) -> None:
    await ws_manager.send_to_project(
        project_id, {"stage": "rendering", "clip_id": clip_id, "progress": progress}
    )


async def emit_analyzed(project_id: str, clips_count: int) -> None:
    await ws_manager.send_to_project(project_id, {"stage": "analyzed", "clips_count": clips_count})


async def emit_clip_ready(project_id: str, clip_id: str, thumbnail_url: str) -> None:
    await ws_manager.send_to_project(
        project_id, {"stage": "clip_ready", "clip_id": clip_id, "thumbnail_url": thumbnail_url}
    )


async def emit_completed(project_id: str) -> None:
    await ws_manager.send_to_project(project_id, {"stage": "completed"})


async def emit_failed(project_id: str, message: str) -> None:
    await ws_manager.send_to_project(project_id, {"stage": "failed", "message": message})
