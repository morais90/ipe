from __future__ import annotations

from florada_payments.auth import build_auth
from florada_payments.resources.charges import (
    AsyncChargesResource,
    ChargesResource,
)
from florada_payments.resources.charges_capture import (
    AsyncChargesCaptureResource,
    ChargesCaptureResource,
)
from florada_payments.resources.charges_refunds import (
    AsyncChargesRefundsResource,
    ChargesRefundsResource,
)
from florada_payments.resources.customers import (
    AsyncCustomersResource,
    CustomersResource,
)
from florada_payments.resources.customers_payment_methods import (
    AsyncCustomersPaymentMethodsResource,
    CustomersPaymentMethodsResource,
)
from florada_payments.resources.customers_subscriptions import (
    AsyncCustomersSubscriptionsResource,
    CustomersSubscriptionsResource,
)
from florada_payments.resources.customers_subscriptions_cancel import (
    AsyncCustomersSubscriptionsCancelResource,
    CustomersSubscriptionsCancelResource,
)
from florada_payments.resources.disputes import (
    AsyncDisputesResource,
    DisputesResource,
)
from florada_payments.resources.disputes_evidence import (
    AsyncDisputesEvidenceResource,
    DisputesEvidenceResource,
)
from florada_payments.resources.plans import (
    AsyncPlansResource,
    PlansResource,
)
from florada_payments.resources.webhooks import (
    AsyncWebhooksResource,
    WebhooksResource,
)
from florada_payments.transport import (
    AsyncHttpxTransport,
    AsyncTransport,
    HttpxTransport,
    Transport,
)


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
        bearer_auth: str | None = None,
        api_key_auth: str | None = None,
        oauth2_client_id: str | None = None,
        oauth2_client_secret: str | None = None,
        timeout: float = 30.0,
        transport: Transport | None = None,
    ) -> None:
        if transport is None:
            headers, params, cookies, auth = build_auth(
                bearer_auth=bearer_auth,
                api_key_auth=api_key_auth,
                oauth2_client_id=oauth2_client_id,
                oauth2_client_secret=oauth2_client_secret,
            )
            transport = HttpxTransport(
                base_url,
                headers=headers,
                params=params,
                cookies=cookies,
                auth=auth,
                timeout=timeout,
            )
        self._transport = transport

        self.charges = ChargesResource(self._transport)
        self.charges_capture = ChargesCaptureResource(self._transport)
        self.charges_refunds = ChargesRefundsResource(self._transport)
        self.customers = CustomersResource(self._transport)
        self.customers_payment_methods = CustomersPaymentMethodsResource(
            self._transport
        )
        self.customers_subscriptions = CustomersSubscriptionsResource(self._transport)
        self.customers_subscriptions_cancel = CustomersSubscriptionsCancelResource(
            self._transport
        )
        self.disputes = DisputesResource(self._transport)
        self.disputes_evidence = DisputesEvidenceResource(self._transport)
        self.plans = PlansResource(self._transport)
        self.webhooks = WebhooksResource(self._transport)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> FloradaPaymentsClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncFloradaPaymentsClient:
    """Florada Payments API client (async).

    Payment processing platform API. Accept payments, manage customers,
    subscriptions, and disputes.

    Usage:
        client = AsyncFloradaPaymentsClient(base_url="https://api.florada.dev/v1")
        await client.charges.list()
        await client.charges_capture.list()
        await client.charges_refunds.list()
        await client.customers.list()
        await client.customers_payment_methods.list()
        await client.customers_subscriptions.list()
        await client.customers_subscriptions_cancel.list()
        await client.disputes.list()
        await client.disputes_evidence.list()
        await client.plans.list()
        await client.webhooks.list()
    """

    def __init__(
        self,
        base_url: str = "https://api.florada.dev/v1",
        *,
        bearer_auth: str | None = None,
        api_key_auth: str | None = None,
        oauth2_client_id: str | None = None,
        oauth2_client_secret: str | None = None,
        timeout: float = 30.0,
        transport: AsyncTransport | None = None,
    ) -> None:
        if transport is None:
            headers, params, cookies, auth = build_auth(
                bearer_auth=bearer_auth,
                api_key_auth=api_key_auth,
                oauth2_client_id=oauth2_client_id,
                oauth2_client_secret=oauth2_client_secret,
            )
            transport = AsyncHttpxTransport(
                base_url,
                headers=headers,
                params=params,
                cookies=cookies,
                auth=auth,
                timeout=timeout,
            )
        self._transport = transport

        self.charges = AsyncChargesResource(self._transport)
        self.charges_capture = AsyncChargesCaptureResource(self._transport)
        self.charges_refunds = AsyncChargesRefundsResource(self._transport)
        self.customers = AsyncCustomersResource(self._transport)
        self.customers_payment_methods = AsyncCustomersPaymentMethodsResource(
            self._transport
        )
        self.customers_subscriptions = AsyncCustomersSubscriptionsResource(
            self._transport
        )
        self.customers_subscriptions_cancel = AsyncCustomersSubscriptionsCancelResource(
            self._transport
        )
        self.disputes = AsyncDisputesResource(self._transport)
        self.disputes_evidence = AsyncDisputesEvidenceResource(self._transport)
        self.plans = AsyncPlansResource(self._transport)
        self.webhooks = AsyncWebhooksResource(self._transport)

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> AsyncFloradaPaymentsClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
