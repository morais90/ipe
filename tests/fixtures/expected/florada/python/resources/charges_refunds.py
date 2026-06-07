"""ChargesRefunds resource."""

from __future__ import annotations

from uuid import UUID

from florada_payments.models.refund import Refund

import httpx


class ChargesRefundsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_charge_refunds(
        self,
        charge_id: UUID,
    ) -> list[Refund]:
        """List refunds for a charge

        Args:
            charge_id: Unique charge identifier
        """
        url = "/charges/{charge_id}/refunds".format(
            charge_id=charge_id,
        )
        response = self._client.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return [Refund.model_validate(item) for item in response.json()]

    def create_refund(
        self,
        charge_id: UUID,
    ) -> Refund:
        """Create a refund

        Refunds a charge fully or partially. Multiple partial refunds are
allowed up to the original charge amount.

        Args:
            charge_id: Unique charge identifier
        """
        url = "/charges/{charge_id}/refunds".format(
            charge_id=charge_id,
        )
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return Refund.model_validate(response.json())

