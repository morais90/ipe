from __future__ import annotations

from uuid import UUID

from florada_payments.exceptions import validated
from florada_payments.models.capture_charge_request import CaptureChargeRequest
from florada_payments.models.charge import Charge
from florada_payments.transport import AsyncTransport, Transport


class ChargesCaptureResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    @validated
    def capture_charge(
        self,
        charge_id: UUID,
        body: CaptureChargeRequest | None = None,
    ) -> Charge:
        """Capture a charge

        Captures a previously authorized charge. Only applicable to card
        payments with capture_method=manual.

        Args:
            charge_id: Unique charge identifier
        """
        url = f"/charges/{charge_id}/capture"
        response = self._transport.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return Charge.model_validate(response.json())


class AsyncChargesCaptureResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @validated
    async def capture_charge(
        self,
        charge_id: UUID,
        body: CaptureChargeRequest | None = None,
    ) -> Charge:
        """Capture a charge

        Captures a previously authorized charge. Only applicable to card
        payments with capture_method=manual.

        Args:
            charge_id: Unique charge identifier
        """
        url = f"/charges/{charge_id}/capture"
        response = await self._transport.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return Charge.model_validate(response.json())
