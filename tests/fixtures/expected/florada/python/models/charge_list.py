from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from florada_payments.models.charge import Charge
    from florada_payments.models.pagination_meta import PaginationMeta


class ChargeList(BaseModel):
    data: list[Charge]
    meta: PaginationMeta
