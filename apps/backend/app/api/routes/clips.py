import re
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse
from app.api.deps import get_current_user
from app.repositories.clips import ClipRepository
from app.repositories.projects import ProjectRepository
from app.integrations.r2 import generate_presigned_download_url
from app.schemas.clip import ClipResponse

router = APIRouter(prefix="/api/clips", tags=["clips"])


@router.get("", response_model=list[ClipResponse])
async def list_clips(
    project_id: str = Query(...),
    user=Depends(get_current_user),
):
    project = ProjectRepository().get_by_id(project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404)
    repo = ClipRepository()
    clips = repo.get_by_project(project_id)
    return [ClipResponse.model_validate(c) for c in clips]


@router.get("/{clip_id}/download")
async def download_clip(
    clip_id: str,
    user=Depends(get_current_user),
):
    clip = ClipRepository().get_by_id(clip_id)
    if not clip:
        raise HTTPException(status_code=404)
    project = ProjectRepository().get_by_id(clip.project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404)
    if not clip.r2_key:
        raise HTTPException(status_code=404, detail="Clip not ready")
    download_url = generate_presigned_download_url(clip.r2_key, expires_in=3600)
    filename = f"{re.sub(r'[^\w\-]', '_', clip.title or 'clip')}.mp4"
    return {"download_url": download_url, "filename": filename}


@router.get("/{clip_id}/thumbnail")
async def thumbnail_clip(
    clip_id: str,
    user=Depends(get_current_user),
):
    clip = ClipRepository().get_by_id(clip_id)
    if not clip:
        raise HTTPException(status_code=404)
    project = ProjectRepository().get_by_id(clip.project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404)
    if not clip.thumbnail_r2_key:
        raise HTTPException(status_code=404, detail="Thumbnail not ready")
    url = generate_presigned_download_url(clip.thumbnail_r2_key, expires_in=86400)
    return RedirectResponse(url=url, status_code=302)
