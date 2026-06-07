from __future__ import annotations

from uuid import UUID

from florada_payments.models.subscription import Subscription

import httpx


class CustomersSubscriptionsCancelResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def cancel_subscription(
        self,
        customer_id: UUID,
        subscription_id: UUID,
    ) -> Subscription:
        """Cancel a subscription

        Cancels a subscription. Can be immediate or at end of current billing
period.

        Args:
            customer_id: Unique customer identifier
            subscription_id: subscription_id
        """
        url = "/customers/{customer_id}/subscriptions/{subscription_id}/cancel".format(
            customer_id=customer_id,
            subscription_id=subscription_id,
        )
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return Subscription.model_validate(response.json())

