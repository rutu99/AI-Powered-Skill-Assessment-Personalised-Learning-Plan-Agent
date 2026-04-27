
import uuid
from datetime import datetime
from typing import Optional


class AssessmentStorage:
    def __init__(self, *args, **kwargs):
        # In-memory only — ignore any path arguments
        self._store: dict[str, dict] = {}

    def save(self, session_id: str, metadata: dict, report: dict) -> str:
        record_id = session_id or str(uuid.uuid4())
        self._store[record_id] = {
            "id":             record_id,
            "date":           metadata.get("date", datetime.now().strftime("%Y-%m-%d %H:%M")),
            "candidate_name": metadata.get("candidate_name", "Unknown"),
            "target_role":    metadata.get("target_role", "Unknown"),
            "overall_score":  report.get("overall_score", 0),
            "report":         report,
        }
        return record_id

    def load(self, record_id: str) -> Optional[dict]:
        rec = self._store.get(record_id)
        return rec["report"] if rec else None

    def list_all(self) -> list[dict]:
        records = [
            {k: v for k, v in rec.items() if k != "report"}
            for rec in self._store.values()
        ]
        records.sort(key=lambda x: x.get("date", ""), reverse=True)
        return records

    def delete(self, record_id: str) -> bool:
        if record_id in self._store:
            del self._store[record_id]
            return True
        return False
