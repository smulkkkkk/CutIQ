from fastapi import APIRouter, Depends, HTTPException, status
from gotrue import User
from app.api.deps import get_current_user
from app.schemas.project import ProjectCreate, ProjectResponse
from app.repositories.projects import ProjectRepository

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
async def list_projects(current_user: User = Depends(get_current_user)):
    repo = ProjectRepository()
    return repo.list_by_user(current_user.id)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate, current_user: User = Depends(get_current_user)
):
    repo = ProjectRepository()
    return repo.create(current_user.id, body.title)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str, current_user: User = Depends(get_current_user)
):
    repo = ProjectRepository()
    project = repo.get_by_id(project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project
