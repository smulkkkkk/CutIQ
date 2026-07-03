from pydantic import BaseModel
from datetime import datetime


class JobResponse(BaseModel):
    id: str
    project_id: str
    type: str
    status: str
    progress: int
    error_message: str | None = None
    arq_job_id: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    model_config = {"from_attributes": True}
