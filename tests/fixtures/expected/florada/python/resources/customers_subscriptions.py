"""CustomersSubscriptions resource."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import httpx


class CustomersSubscriptionsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_subscriptions(
        self,
        customer_id: UUID,
        status: str | None = None,
    ) -> Any:
        """List subscriptions for a customer

        Args:
            customer_id: Unique customer identifier
            status: status
        """
        url = "/customers/{customer_id}/subscriptions".format(
            customer_id=customer_id,
        )
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
        customer_id: UUID,
    ) -> Any:
        """Create a subscription

        Subscribes a customer to a plan. First invoice is created immediately.

        Args:
            customer_id: Unique customer identifier
        """
        url = "/customers/{customer_id}/subscriptions".format(
            customer_id=customer_id,
        )
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return response.json()

