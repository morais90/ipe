"""BoletoDetails model."""

from __future__ import annotations

from pydantic import BaseModel


class BoletoDetails(BaseModel):
    barcode: str | None = None
    due_date: date | None = None
    pdf_url: str | None = None
