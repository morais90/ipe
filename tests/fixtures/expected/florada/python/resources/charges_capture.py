from __future__ import annotations

from uuid import UUID

import httpx
from florada_payments.models.charge import Charge


class ChargesCaptureResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def capture_charge(
        self,
        charge_id: UUID,
    ) -> Charge:
        """Capture a charge

        Captures a previously authorized charge. Only applicable to card
        payments with capture_method=manual.

        Args:
            charge_id: Unique charge identifier
        """
        url = f"/charges/{charge_id}/capture"
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return Charge.model_validate(response.json())
