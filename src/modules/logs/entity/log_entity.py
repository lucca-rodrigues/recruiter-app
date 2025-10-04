"""Domain entities for usage logs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass(slots=True)
class UsageLog:
    request_id: str
    user_id: str
    result: str
    query: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_document(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "result": self.result,
            "query": self.query,
            "timestamp": self.timestamp,
        }
