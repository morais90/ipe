from __future__ import annotations

from uuid import UUID

from florada_payments.models.payment_method import PaymentMethod

import httpx


class CustomersPaymentMethodsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_payment_methods(
        self,
        customer_id: UUID,
        type_: str | None = None,
    ) -> list[PaymentMethod]:
        """List payment methods for a customer

        Args:
            customer_id: Unique customer identifier
            type_: Filter by payment method type
        """
        url = "/customers/{customer_id}/payment-methods".format(
            customer_id=customer_id,
        )
        response = self._client.request(
            "GET",
            url,
            params={
                "type": type_,
            },
        )
        response.raise_for_status()
        return [PaymentMethod.model_validate(item) for item in response.json()]

    def attach_payment_method(
        self,
        customer_id: UUID,
    ) -> PaymentMethod:
        """Attach a payment method to a customer

        Args:
            customer_id: Unique customer identifier
        """
        url = "/customers/{customer_id}/payment-methods".format(
            customer_id=customer_id,
        )
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return PaymentMethod.model_validate(response.json())

    def detach_payment_method(
        self,
        customer_id: UUID,
        method_id: UUID,
    ) -> None:
        """Detach a payment method

        Args:
            customer_id: Unique customer identifier
            method_id: method_id
        """
        url = "/customers/{customer_id}/payment-methods/{method_id}".format(
            customer_id=customer_id,
            method_id=method_id,
        )
        response = self._client.request(
            "DELETE",
            url,
        )
        response.raise_for_status()
        return None

