"""CreateWebhookRequest model."""

from __future__ import annotations

from pydantic import BaseModel


class CreateWebhookRequest(BaseModel):
    url: str
    events: list
