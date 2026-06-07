from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class Money(BaseModel):
    amount: Annotated[int, Field(ge=0)]
    currency: Annotated[str, Field(min_length=3, max_length=3, pattern="^[A-Z]{3}$")]
