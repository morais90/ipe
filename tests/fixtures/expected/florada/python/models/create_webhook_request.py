from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class CreateWebhookRequest(BaseModel):
    url: str
    events: Annotated[list, Field(min_length=1)]
