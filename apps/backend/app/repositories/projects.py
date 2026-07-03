from datetime import datetime
from app.repositories.base import BaseRepository
from app.core.supabase import get_supabase
from app.models.project import Project


class ProjectRepository(BaseRepository):
    def __init__(self):
        self.table = "projects"
        self.client = get_supabase()

    def create(self, user_id: str, title: str) -> Project:
        response = (
            self.client.table(self.table)
            .insert({"user_id": user_id, "title": title, "status": "created"})
            .execute()
        )
        return self._to_model(response.data[0])

    def get_by_id(self, project_id: str) -> Project | None:
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("id", project_id)
            .single()
            .execute()
        )
        if not response.data:
            return None
        return self._to_model(response.data)

    def list_by_user(self, user_id: str, limit: int = 20) -> list[Project]:
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [self._to_model(row) for row in response.data]

    def update_status(self, project_id: str, status: str) -> Project:
        response = (
            self.client.table(self.table)
            .update({"status": status, "updated_at": datetime.utcnow().isoformat()})
            .eq("id", project_id)
            .execute()
        )
        return self._to_model(response.data[0])

    def _to_model(self, data: dict) -> Project:
        return Project(
            id=data["id"],
            user_id=data["user_id"],
            title=data["title"],
            status=data["status"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
