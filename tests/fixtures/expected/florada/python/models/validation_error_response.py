from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

if TYPE_CHECKING:
    from florada_payments.models.field_error import FieldError


class ValidationErrorResponse(BaseModel):
    code: Literal["validation_error"]
    message: str
    errors: list[FieldError]
