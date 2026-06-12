from __future__ import annotations

from uuid import UUID

from florada_payments.exceptions import validated
from florada_payments.models.create_refund_request import CreateRefundRequest
from florada_payments.models.refund import Refund
from florada_payments.transport import AsyncTransport, Transport


class ChargesRefundsResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    @validated
    def list_charge_refunds(
        self,
        charge_id: UUID,
    ) -> list[Refund]:
        """List refunds for a charge

        Args:
            charge_id: Unique charge identifier
        """
        url = f"/charges/{charge_id}/refunds"
        response = self._transport.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return [Refund.model_validate(item) for item in response.json()]

    @validated
    def create_refund(
        self,
        charge_id: UUID,
        body: CreateRefundRequest,
    ) -> Refund:
        """Create a refund

        Refunds a charge fully or partially. Multiple partial refunds
        are allowed up to the original charge amount.

        Args:
            charge_id: Unique charge identifier
        """
        url = f"/charges/{charge_id}/refunds"
        response = self._transport.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return Refund.model_validate(response.json())


class AsyncChargesRefundsResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @validated
    async def list_charge_refunds(
        self,
        charge_id: UUID,
    ) -> list[Refund]:
        """List refunds for a charge

        Args:
            charge_id: Unique charge identifier
        """
        url = f"/charges/{charge_id}/refunds"
        response = await self._transport.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return [Refund.model_validate(item) for item in response.json()]

    @validated
    async def create_refund(
        self,
        charge_id: UUID,
        body: CreateRefundRequest,
    ) -> Refund:
        """Create a refund

        Refunds a charge fully or partially. Multiple partial refunds
        are allowed up to the original charge amount.

        Args:
            charge_id: Unique charge identifier
        """
        url = f"/charges/{charge_id}/refunds"
        response = await self._transport.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return Refund.model_validate(response.json())
