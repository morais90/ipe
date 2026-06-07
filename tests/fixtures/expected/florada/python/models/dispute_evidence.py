from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class DisputeEvidence(BaseModel):
    description: Annotated[str, Field(max_length=5000)] | None = None
    receipt_url: str | None = None
    shipping_tracking: str | None = None
    customer_communication: str | None = None
