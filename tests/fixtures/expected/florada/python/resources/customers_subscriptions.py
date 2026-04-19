"""CustomersSubscriptions resource."""

from __future__ import annotations

from typing import Any

import httpx


class CustomersSubscriptionsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_subscriptions(
        self,
        status: str | None = None,
    ) -> Any:
        """List subscriptions for a customer

        Args:
            status: status
        """
        url = "/customers/{customer_id}/subscriptions"
        response = self._client.request(
            "GET",
            url,
            params={
                "status": status,
            },
        )
        response.raise_for_status()
        return response.json()

    def create_subscription(
        self,
    ) -> Any:
        """Create a subscription

        Subscribes a customer to a plan. First invoice is created immediately.
        """
        url = "/customers/{customer_id}/subscriptions"
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return response.json()

