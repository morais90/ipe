"""ChargesRefunds resource."""

from __future__ import annotations

from typing import Any

import httpx


class ChargesRefundsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_charge_refunds(
        self,
    ) -> Any:
        """List refunds for a charge"""
        url = "/charges/{charge_id}/refunds"
        response = self._client.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return response.json()

    def create_refund(
        self,
    ) -> Any:
        """Create a refund

        Refunds a charge fully or partially. Multiple partial refunds are
allowed up to the original charge amount.
        """
        url = "/charges/{charge_id}/refunds"
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return response.json()

