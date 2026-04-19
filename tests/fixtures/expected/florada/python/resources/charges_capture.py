"""ChargesCapture resource."""

from __future__ import annotations

from typing import Any

import httpx


class ChargesCaptureResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def capture_charge(
        self,
    ) -> Any:
        """Capture a charge

        Captures a previously authorized charge. Only applicable to card
payments with capture_method=manual.
        """
        url = "/charges/{charge_id}/capture"
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return response.json()

