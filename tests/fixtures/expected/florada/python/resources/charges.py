from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from florada_payments.exceptions import validated
from florada_payments.models.charge import Charge
from florada_payments.models.charge_list import ChargeList
from florada_payments.models.create_charge_request import CreateChargeRequest
from florada_payments.transport import AsyncTransport, Transport
from pydantic import Field


class ChargesResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    @validated
    def list_charges(
        self,
        status: Literal["pending", "succeeded", "failed", "refunded", "disputed"]
        | None = None,
        customer_id: UUID | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        limit: Annotated[int, Field(ge=1, le=100)] | None = 20,
        cursor: str | None = None,
    ) -> ChargeList:
        """List charges

        Returns a paginated list of charges. Supports filtering by
        status, customer, and date range.

        Args:
            status: Filter by charge status
            customer_id: Filter by customer
            created_after: Filter charges created after this date
            created_before: Filter charges created before this date
            limit: Maximum number of results (1-100)
            cursor: Pagination cursor
        """
        url = "/charges"
        response = self._transport.request(
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

    @validated
    def create_charge(
        self,
        body: CreateChargeRequest,
    ) -> Charge:
        """Create a charge

        Creates a new payment charge. The charge is processed
        immediately for card payments, or generates a payment voucher
        for boleto/pix.
        """
        url = "/charges"
        response = self._transport.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return Charge.model_validate(response.json())

    @validated
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
        url = f"/charges/{charge_id}"
        response = self._transport.request(
            "GET",
            url,
            params={
                "expand": expand,
            },
        )
        response.raise_for_status()
        return Charge.model_validate(response.json())


class AsyncChargesResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @validated
    async def list_charges(
        self,
        status: Literal["pending", "succeeded", "failed", "refunded", "disputed"]
        | None = None,
        customer_id: UUID | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        limit: Annotated[int, Field(ge=1, le=100)] | None = 20,
        cursor: str | None = None,
    ) -> ChargeList:
        """List charges

        Returns a paginated list of charges. Supports filtering by
        status, customer, and date range.

        Args:
            status: Filter by charge status
            customer_id: Filter by customer
            created_after: Filter charges created after this date
            created_before: Filter charges created before this date
            limit: Maximum number of results (1-100)
            cursor: Pagination cursor
        """
        url = "/charges"
        response = await self._transport.request(
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

    @validated
    async def create_charge(
        self,
        body: CreateChargeRequest,
    ) -> Charge:
        """Create a charge

        Creates a new payment charge. The charge is processed
        immediately for card payments, or generates a payment voucher
        for boleto/pix.
        """
        url = "/charges"
        response = await self._transport.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return Charge.model_validate(response.json())

    @validated
    async def get_charge(
        self,
        charge_id: UUID,
        expand: list | None = None,
    ) -> Charge:
        """Retrieve a charge

        Args:
            charge_id: Unique charge identifier
            expand: Related resources to include in the response
        """
        url = f"/charges/{charge_id}"
        response = await self._transport.request(
            "GET",
            url,
            params={
                "expand": expand,
            },
        )
        response.raise_for_status()
        return Charge.model_validate(response.json())
