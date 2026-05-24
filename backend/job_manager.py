import uuid
from typing import Any

_jobs: dict[str, dict[str, Any]] = {}

def create_job() -> str:
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending", "progress": 0, "message": "", "result": None, "error": None}
    return job_id

def update_job(job_id: str, **kwargs: Any) -> None:
    if job_id in _jobs:
        _jobs[job_id].update(kwargs)

def get_job(job_id: str) -> dict[str, Any] | None:
    return _jobs.get(job_id)