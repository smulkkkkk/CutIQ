from dataclasses import dataclass
from datetime import datetime

@dataclass
class Profile:
    id: str
    full_name: str | None
    avatar_url: str | None
    plan: str
    credits_used: int
    credits_limit: int
    is_admin: bool
    stripe_customer_id: str | None
    created_at: datetime
    updated_at: datetime
