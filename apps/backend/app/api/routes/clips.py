from fastapi import APIRouter, Depends, Query
from app.api.deps import get_current_user
from app.repositories.clips import ClipRepository
from app.schemas.clip import ClipResponse

router = APIRouter(prefix="/api/clips", tags=["clips"])


@router.get("", response_model=list[ClipResponse])
async def list_clips(
    project_id: str = Query(...),
    user=Depends(get_current_user),
):
    repo = ClipRepository()
    clips = repo.get_by_project(project_id)
    return [ClipResponse.model_validate(c) for c in clips]
