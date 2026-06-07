from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ValidationErrorResponse(BaseModel):
    code: Literal["validation_error"]
    message: str
    errors: list
