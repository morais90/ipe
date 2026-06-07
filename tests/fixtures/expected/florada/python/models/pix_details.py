from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class PixDetails(BaseModel):
    key_type: Literal["cpf", "cnpj", "email", "phone", "random"] | None = None
    key: str | None = None
