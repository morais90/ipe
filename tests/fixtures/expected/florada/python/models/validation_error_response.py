from __future__ import annotations

from pydantic import BaseModel


class ValidationErrorResponse(BaseModel):
    code: str
    message: str
    errors: list
