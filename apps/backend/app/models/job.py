from dataclasses import dataclass
from datetime import datetime


@dataclass
class Job:
    id: str
    project_id: str
    type: str
    status: str
    progress: int
    error_message: str | None
    arq_job_id: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
