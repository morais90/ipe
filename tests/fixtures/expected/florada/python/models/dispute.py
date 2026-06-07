from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Dispute(BaseModel):
    id: UUID
    charge_id: UUID
    amount: dict[str, Any]
    status: str
    reason: str
    evidence: dict[str, Any] | None = None
    evidence_due_by: datetime | None = None
    created_at: datetime
    resolved_at: datetime | None = None
