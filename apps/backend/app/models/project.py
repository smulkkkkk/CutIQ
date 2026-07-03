from dataclasses import dataclass
from datetime import datetime


@dataclass
class Project:
    id: str
    user_id: str
    title: str
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Video:
    id: str
    project_id: str
    user_id: str
    source_type: str
    filename: str
    status: str
    source_url: str | None
    r2_key: str | None
    duration_seconds: float | None
    size_bytes: int | None
    created_at: datetime
