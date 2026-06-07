from __future__ import annotations

from typing import Literal
from uuid import UUID

import httpx
from florada_payments.exceptions import validated
from florada_payments.models.attach_payment_method_request import (
    AttachPaymentMethodRequest,
)
from florada_payments.models.payment_method import PaymentMethod


class CustomersPaymentMethodsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    @validated
    def list_payment_methods(
        self,
        customer_id: UUID,
        type_: Literal["card", "pix", "boleto"] | None = None,
    ) -> list[PaymentMethod]:
        """List payment methods for a customer

        Args:
            customer_id: Unique customer identifier
            type_: Filter by payment method type
        """
        url = f"/customers/{customer_id}/payment-methods"
        response = self._client.request(
            "GET",
            url,
            params={
                "type": type_,
            },
        )
        response.raise_for_status()
        return [PaymentMethod.model_validate(item) for item in response.json()]

    @validated
    def attach_payment_method(
        self,
        customer_id: UUID,
        body: AttachPaymentMethodRequest,
    ) -> PaymentMethod:
        """Attach a payment method to a customer

        Args:
            customer_id: Unique customer identifier
        """
        url = f"/customers/{customer_id}/payment-methods"
        response = self._client.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return PaymentMethod.model_validate(response.json())

    @validated
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
        url = f"/customers/{customer_id}/payment-methods/{method_id}"
        response = self._client.request(
            "DELETE",
            url,
        )
        response.raise_for_status()
        return None
