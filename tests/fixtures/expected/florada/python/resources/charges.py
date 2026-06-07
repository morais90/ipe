from __future__ import annotations

from datetime import datetime
from uuid import UUID

from florada_payments.models.charge import Charge
from florada_payments.models.charge_list import ChargeList

import httpx


class ChargesResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_charges(
        self,
        status: str | None = None,
        customer_id: UUID | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        limit: int | None = 20,
        cursor: str | None = None,
    ) -> ChargeList:
        """List charges

        Returns a paginated list of charges. Supports filtering by status,
customer, and date range.

        Args:
            status: Filter by charge status
            customer_id: Filter by customer
            created_after: Filter charges created after this date
            created_before: Filter charges created before this date
            limit: Maximum number of results (1-100)
            cursor: Pagination cursor
        """
        url = "/charges"
        response = self._client.request(
            "GET",
            url,
            params={
                "status": status,
                "customer_id": customer_id,
                "created_after": created_after,
                "created_before": created_before,
                "limit": limit,
                "cursor": cursor,
            },
        )
        response.raise_for_status()
        return ChargeList.model_validate(response.json())

    def create_charge(
        self,
    ) -> Charge:
        """Create a charge

        Creates a new payment charge. The charge is processed immediately for
card payments, or generates a payment voucher for boleto/pix.
        """
        url = "/charges"
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return Charge.model_validate(response.json())

    def get_charge(
        self,
        charge_id: UUID,
        expand: list | None = None,
    ) -> Charge:
        """Retrieve a charge

        Args:
            charge_id: Unique charge identifier
            expand: Related resources to include in the response
        """
        url = "/charges/{charge_id}".format(
            charge_id=charge_id,
        )
        response = self._client.request(
            "GET",
            url,
            params={
                "expand": expand,
            },
        )
        response.raise_for_status()
        return Charge.model_validate(response.json())

