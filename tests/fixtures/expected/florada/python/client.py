"""Florada Payments API client."""

from __future__ import annotations

import httpx

from florada_payments.resources.charges import ChargesResource
from florada_payments.resources.charges_capture import ChargesCaptureResource
from florada_payments.resources.charges_refunds import ChargesRefundsResource
from florada_payments.resources.customers import CustomersResource
from florada_payments.resources.customers_payment_methods import CustomersPaymentMethodsResource
from florada_payments.resources.customers_subscriptions import CustomersSubscriptionsResource
from florada_payments.resources.customers_subscriptions_cancel import CustomersSubscriptionsCancelResource
from florada_payments.resources.disputes import DisputesResource
from florada_payments.resources.disputes_evidence import DisputesEvidenceResource
from florada_payments.resources.plans import PlansResource
from florada_payments.resources.webhooks import WebhooksResource


class FloradaPaymentsClient:
    """Florada Payments API client.

    Payment processing platform API. Accept payments, manage customers,
subscriptions, and disputes.

    Usage:
        client = FloradaPaymentsClient(base_url="https://api.florada.dev/v1")
        client.charges.list()
        client.charges_capture.list()
        client.charges_refunds.list()
        client.customers.list()
        client.customers_payment_methods.list()
        client.customers_subscriptions.list()
        client.customers_subscriptions_cancel.list()
        client.disputes.list()
        client.disputes_evidence.list()
        client.plans.list()
        client.webhooks.list()
    """

    def __init__(
        self,
        base_url: str = "https://api.florada.dev/v1",
        *,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
        )
        if api_key:
            self._client.headers["Authorization"] = f"Bearer {api_key}"

        self.charges = ChargesResource(self._client)
        self.charges_capture = ChargesCaptureResource(self._client)
        self.charges_refunds = ChargesRefundsResource(self._client)
        self.customers = CustomersResource(self._client)
        self.customers_payment_methods = CustomersPaymentMethodsResource(self._client)
        self.customers_subscriptions = CustomersSubscriptionsResource(self._client)
        self.customers_subscriptions_cancel = CustomersSubscriptionsCancelResource(self._client)
        self.disputes = DisputesResource(self._client)
        self.disputes_evidence = DisputesEvidenceResource(self._client)
        self.plans = PlansResource(self._client)
        self.webhooks = WebhooksResource(self._client)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> FloradaPaymentsClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
