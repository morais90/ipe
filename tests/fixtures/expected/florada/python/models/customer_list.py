"""CustomerList model."""

from __future__ import annotations

from pydantic import BaseModel


class CustomerList(BaseModel):
    data: list
    meta: dict[str, Any]
