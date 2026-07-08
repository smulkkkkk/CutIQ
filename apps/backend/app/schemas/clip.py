from pydantic import BaseModel
from datetime import datetime


class ClipResponse(BaseModel):
    id: str
    project_id: str
    video_id: str
    title: str | None
    start_time: float
    end_time: float
    duration: float
    virality_score: int | None
    virality_reasons: list[str] | None
    status: str
    r2_key: str | None
    thumbnail_r2_key: str | None
    resolution: str
    has_watermark: bool
    caption_style: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
