"""WebhookEndpoint model."""

from __future__ import annotations

from pydantic import BaseModel


class WebhookEndpoint(BaseModel):
    id: UUID
    url: str
    events: list
    secret: str | None = None
    active: bool = true
