from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from florada_payments.models.dispute_evidence import DisputeEvidence
    from florada_payments.models.money import Money


class Dispute(BaseModel):
    id: UUID
    charge_id: UUID
    amount: Money
    status: Literal["open", "under_review", "won", "lost"]
    reason: Literal[
        "fraudulent", "duplicate", "not_received", "product_not_as_described", "other"
    ]
    evidence: DisputeEvidence | None = None
    evidence_due_by: datetime | None = None
    created_at: datetime
    resolved_at: datetime | None = None
