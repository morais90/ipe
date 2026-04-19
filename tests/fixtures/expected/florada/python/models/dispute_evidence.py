"""DisputeEvidence model."""

from __future__ import annotations

from pydantic import BaseModel


class DisputeEvidence(BaseModel):
    description: str | None = None
    receipt_url: str | None = None
    shipping_tracking: str | None = None
    customer_communication: str | None = None
