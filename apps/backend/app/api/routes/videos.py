import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from gotrue import User
from app.api.deps import get_current_user
from app.schemas.project import (
    VideoCreateRequest,
    CreateVideoResponse,
    VideoResponse,
    YoutubeImportRequest,
)
from app.repositories.projects import ProjectRepository
from app.repositories.videos import VideoRepository
from app.repositories.jobs import JobRepository
from app.integrations.r2 import generate_presigned_upload_url

router = APIRouter()


async def enqueue_transcription(video_id: str, project_id: str) -> str:
    """Stub: returns a fake job_id. Task 6 replaces this with real ARQ."""
    return str(uuid.uuid4())


@router.post("", response_model=CreateVideoResponse)
async def create_video(
    body: VideoCreateRequest, current_user: User = Depends(get_current_user)
):
    proj_repo = ProjectRepository()
    project = proj_repo.get_by_id(body.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    r2_key = f"videos/{current_user.id}/{body.project_id}/{uuid.uuid4()}/{body.filename}"
    vid_repo = VideoRepository()
    video = vid_repo.create(
        project_id=body.project_id,
        user_id=current_user.id,
        source_type="upload",
        filename=body.filename,
        r2_key=r2_key,
    )
    upload_url = generate_presigned_upload_url(r2_key, content_type=body.content_type)
    return CreateVideoResponse(id=video.id, upload_url=upload_url, r2_key=r2_key)


@router.post("/import-youtube", response_model=VideoResponse)
async def import_youtube(
    body: YoutubeImportRequest, current_user: User = Depends(get_current_user)
):
    proj_repo = ProjectRepository()
    project = proj_repo.get_by_id(body.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    from app.integrations.youtube import get_youtube_info
    try:
        info = await get_youtube_info(body.url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid YouTube URL: {e}",
        )

    r2_key = f"videos/{current_user.id}/{body.project_id}/{uuid.uuid4()}/youtube.mp4"
    vid_repo = VideoRepository()
    video = vid_repo.create(
        project_id=body.project_id,
        user_id=current_user.id,
        source_type="youtube",
        filename=f"{info['title']}.mp4",
        r2_key=r2_key,
        source_url=body.url,
    )

    arq_job_id = await enqueue_transcription(video.id, body.project_id)
    job_repo = JobRepository()
    job_repo.create(body.project_id, "download_youtube", arq_job_id=arq_job_id)

    return video


@router.post("/{video_id}/process")
async def process_video(
    video_id: str, current_user: User = Depends(get_current_user)
):
    vid_repo = VideoRepository()
    video = vid_repo.get_by_id(video_id)
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    vid_repo.update(video_id, status="processing")
    arq_job_id = await enqueue_transcription(video_id, video.project_id)

    job_repo = JobRepository()
    job_repo.create(video.project_id, "transcribe", arq_job_id=arq_job_id)

    return {"status": "processing", "video_id": video_id}
