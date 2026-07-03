from fastapi import APIRouter, Depends, HTTPException, status
from gotrue import User
from app.api.deps import get_current_user
from app.repositories.users import UserRepository
from app.schemas.auth import ProfileResponse

router = APIRouter()

@router.get("/me", response_model=ProfileResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    repo = UserRepository()
    profile = repo.get_by_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Contact support.",
        )
    return profile
