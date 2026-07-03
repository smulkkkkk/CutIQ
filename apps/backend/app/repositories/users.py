from datetime import datetime
from app.repositories.base import BaseRepository
from app.models.user import Profile

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__("profiles")

    def get_by_id(self, user_id: str) -> Profile | None:
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )
        if not response.data:
            return None
        return self._to_model(response.data)

    def upsert_profile(self, user_id: str, full_name: str | None = None) -> Profile:
        self.client.table(self.table).upsert(
            {"id": user_id, "full_name": full_name}
        ).execute()
        return self.get_by_id(user_id)

    def _to_model(self, data: dict) -> Profile:
        return Profile(
            id=data["id"],
            full_name=data.get("full_name"),
            avatar_url=data.get("avatar_url"),
            plan=data["plan"],
            credits_used=data["credits_used"],
            credits_limit=data["credits_limit"],
            is_admin=data["is_admin"],
            stripe_customer_id=data.get("stripe_customer_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
