from __future__ import annotations

from typing import Literal
from uuid import UUID

import httpx
from florada_payments.exceptions import validated
from florada_payments.models.create_subscription_request import (
    CreateSubscriptionRequest,
)
from florada_payments.models.subscription import Subscription


class CustomersSubscriptionsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    @validated
    def list_subscriptions(
        self,
        customer_id: UUID,
        status: Literal["active", "past_due", "cancelled", "trialing"] | None = None,
    ) -> list[Subscription]:
        """List subscriptions for a customer

        Args:
            customer_id: Unique customer identifier
            status: status
        """
        url = f"/customers/{customer_id}/subscriptions"
        response = self._client.request(
            "GET",
            url,
            params={
                "status": status,
            },
        )
        response.raise_for_status()
        return [Subscription.model_validate(item) for item in response.json()]

    @validated
    def create_subscription(
        self,
        customer_id: UUID,
        body: CreateSubscriptionRequest,
    ) -> Subscription:
        """Create a subscription

        Subscribes a customer to a plan. First invoice is created
        immediately.

        Args:
            customer_id: Unique customer identifier
        """
        url = f"/customers/{customer_id}/subscriptions"
        response = self._client.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return Subscription.model_validate(response.json())
