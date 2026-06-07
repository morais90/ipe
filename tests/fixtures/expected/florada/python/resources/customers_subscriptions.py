from __future__ import annotations

from uuid import UUID

from florada_payments.models.subscription import Subscription

import httpx


class CustomersSubscriptionsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_subscriptions(
        self,
        customer_id: UUID,
        status: str | None = None,
    ) -> list[Subscription]:
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
        return [Subscription.model_validate(item) for item in response.json()]

    def create_subscription(
        self,
        customer_id: UUID,
    ) -> Subscription:
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
        return Subscription.model_validate(response.json())

