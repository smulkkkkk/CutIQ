from datetime import datetime, timezone
from app.repositories.base import BaseRepository
from app.core.supabase import get_supabase
from app.models.clip import Clip


class ClipRepository(BaseRepository):
    def __init__(self):
        self.table = "clips"
        self.client = get_supabase()

    def create(
        self,
        project_id: str,
        video_id: str,
        title: str | None,
        start_time: float,
        end_time: float,
        virality_score: int | None,
        virality_reasons: list[str] | None,
    ) -> Clip:
        response = (
            self.client.table(self.table)
            .insert({
                "project_id": project_id,
                "video_id": video_id,
                "title": title,
                "start_time": start_time,
                "end_time": end_time,
                "virality_score": virality_score,
                "virality_reasons": virality_reasons,
                "status": "pending",
            })
            .execute()
        )
        return self._to_model(response.data[0])

    def get_by_project(self, project_id: str) -> list[Clip]:
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("project_id", project_id)
            .order("virality_score", desc=True)
            .execute()
        )
        return [self._to_model(row) for row in response.data]

    def get_by_id(self, clip_id: str) -> Clip | None:
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("id", clip_id)
            .maybe_single()
            .execute()
        )
        if not response.data:
            return None
        return self._to_model(response.data)

    def update(self, clip_id: str, **kwargs) -> Clip:
        kwargs["updated_at"] = datetime.now(timezone.utc).isoformat()
        response = (
            self.client.table(self.table)
            .update(kwargs)
            .eq("id", clip_id)
            .execute()
        )
        return self._to_model(response.data[0])

    def _to_model(self, data: dict) -> Clip:
        return Clip(
            id=data["id"],
            project_id=data["project_id"],
            video_id=data["video_id"],
            title=data.get("title"),
            start_time=float(data["start_time"]),
            end_time=float(data["end_time"]),
            duration=float(data.get("duration") or 0.0),
            virality_score=data.get("virality_score"),
            virality_reasons=data.get("virality_reasons"),
            status=data["status"],
            r2_key=data.get("r2_key"),
            thumbnail_r2_key=data.get("thumbnail_r2_key"),
            resolution=data.get("resolution", "720p"),
            has_watermark=bool(data.get("has_watermark", True)),
            caption_style=data.get("caption_style", "default"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
