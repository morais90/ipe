from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class WebhookEndpoint(BaseModel):
    id: UUID
    url: str
    events: list
    secret: str | None = None
    active: bool = True
