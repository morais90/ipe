from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from florada_payments.models.customer import Customer
    from florada_payments.models.pagination_meta import PaginationMeta


class CustomerList(BaseModel):
    data: list[Customer]
    meta: PaginationMeta
