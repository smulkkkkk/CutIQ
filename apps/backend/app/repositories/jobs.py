from datetime import datetime
from app.repositories.base import BaseRepository
from app.models.job import Job


class JobRepository(BaseRepository):
    def __init__(self):
        super().__init__("jobs")

    def create(self, project_id: str, job_type: str, arq_job_id: str | None = None) -> Job:
        response = (
            self.client.table(self.table)
            .insert({
                "project_id": project_id,
                "type": job_type,
                "status": "queued",
                "progress": 0,
                "arq_job_id": arq_job_id,
            })
            .execute()
        )
        return self._to_model(response.data[0])

    def update(self, job_id: str, **kwargs) -> Job:
        response = (
            self.client.table(self.table)
            .update(kwargs)
            .eq("id", job_id)
            .execute()
        )
        return self._to_model(response.data[0])

    def get_by_project(self, project_id: str) -> list[Job]:
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("project_id", project_id)
            .order("created_at", desc=True)
            .execute()
        )
        return [self._to_model(row) for row in response.data]

    def _to_model(self, data: dict) -> Job:
        def _dt(val):
            return datetime.fromisoformat(val) if val else None

        return Job(
            id=data["id"],
            project_id=data["project_id"],
            type=data["type"],
            status=data["status"],
            progress=data["progress"],
            error_message=data.get("error_message"),
            arq_job_id=data.get("arq_job_id"),
            started_at=_dt(data.get("started_at")),
            completed_at=_dt(data.get("completed_at")),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
