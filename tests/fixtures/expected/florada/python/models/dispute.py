from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel


class Dispute(BaseModel):
    id: UUID
    charge_id: UUID
    amount: dict[str, Any]
    status: Literal["open", "under_review", "won", "lost"]
    reason: Literal[
        "fraudulent", "duplicate", "not_received", "product_not_as_described", "other"
    ]
    evidence: dict[str, Any] | None = None
    evidence_due_by: datetime | None = None
    created_at: datetime
    resolved_at: datetime | None = None
