from pydantic import BaseModel
from datetime import datetime

class ProfileResponse(BaseModel):
    id: str
    full_name: str | None = None
    avatar_url: str | None = None
    plan: str
    credits_used: int
    credits_limit: int
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
