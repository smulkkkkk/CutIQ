from pydantic import BaseModel
from datetime import datetime


class ProjectCreate(BaseModel):
    title: str


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    title: str
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class VideoResponse(BaseModel):
    id: str
    project_id: str
    source_type: str
    filename: str
    status: str
    source_url: str | None = None
    r2_key: str | None = None
    duration_seconds: float | None = None
    size_bytes: int | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class VideoCreateRequest(BaseModel):
    project_id: str
    filename: str
    content_type: str = "video/mp4"


class CreateVideoResponse(BaseModel):
    id: str
    upload_url: str
    r2_key: str


class YoutubeImportRequest(BaseModel):
    project_id: str
    url: str
