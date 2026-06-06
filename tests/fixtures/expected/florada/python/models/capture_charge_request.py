"""CaptureChargeRequest model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class CaptureChargeRequest(BaseModel):
    amount: dict[str, Any] | None = None
