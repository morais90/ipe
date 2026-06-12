from __future__ import annotations

from uuid import UUID

from florada_payments.exceptions import validated
from florada_payments.models.cancel_subscription_request import (
    CancelSubscriptionRequest,
)
from florada_payments.models.subscription import Subscription
from florada_payments.transport import AsyncTransport, Transport


class CustomersSubscriptionsCancelResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    @validated
    def cancel_subscription(
        self,
        customer_id: UUID,
        subscription_id: UUID,
        body: CancelSubscriptionRequest | None = None,
    ) -> Subscription:
        """Cancel a subscription

        Cancels a subscription. Can be immediate or at end of current
        billing period.

        Args:
            customer_id: Unique customer identifier
            subscription_id: subscription_id
        """
        url = f"/customers/{customer_id}/subscriptions/{subscription_id}/cancel"
        response = self._transport.request(
            "POST",
            url,
            json=body.model_dump(mode="json") if body is not None else None,
        )
        response.raise_for_status()
        return Subscription.model_validate(response.json())


class AsyncCustomersSubscriptionsCancelResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @validated
    async def cancel_subscription(
        self,
        customer_id: UUID,
        subscription_id: UUID,
        body: CancelSubscriptionRequest | None = None,
    ) -> Subscription:
        """Cancel a subscription

        Cancels a subscription. Can be immediate or at end of current
        billing period.

        Args:
            customer_id: Unique customer identifier
            subscription_id: subscription_id
        """
        url = f"/customers/{customer_id}/subscriptions/{subscription_id}/cancel"
        response = await self._transport.request(
            "POST",
            url,
            json=body.model_dump(mode="json") if body is not None else None,
        )
        response.raise_for_status()
        return Subscription.model_validate(response.json())
