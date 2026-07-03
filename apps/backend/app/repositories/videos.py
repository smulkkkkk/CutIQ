from datetime import datetime
from app.repositories.base import BaseRepository
from app.core.supabase import get_supabase
from app.models.project import Video


class VideoRepository(BaseRepository):
    def __init__(self):
        self.table = "videos"
        self.client = get_supabase()

    def create(
        self,
        project_id: str,
        user_id: str,
        source_type: str,
        filename: str,
        r2_key: str | None = None,
        source_url: str | None = None,
    ) -> Video:
        response = (
            self.client.table(self.table)
            .insert({
                "project_id": project_id,
                "user_id": user_id,
                "source_type": source_type,
                "filename": filename,
                "r2_key": r2_key,
                "source_url": source_url,
                "status": "pending",
            })
            .execute()
        )
        return self._to_model(response.data[0])

    def get_by_id(self, video_id: str) -> Video | None:
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("id", video_id)
            .single()
            .execute()
        )
        if not response.data:
            return None
        return self._to_model(response.data)

    def update(self, video_id: str, **kwargs) -> Video:
        response = (
            self.client.table(self.table)
            .update(kwargs)
            .eq("id", video_id)
            .execute()
        )
        return self._to_model(response.data[0])

    def _to_model(self, data: dict) -> Video:
        return Video(
            id=data["id"],
            project_id=data["project_id"],
            user_id=data["user_id"],
            source_type=data["source_type"],
            filename=data["filename"],
            status=data["status"],
            source_url=data.get("source_url"),
            r2_key=data.get("r2_key"),
            duration_seconds=data.get("duration_seconds"),
            size_bytes=data.get("size_bytes"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
