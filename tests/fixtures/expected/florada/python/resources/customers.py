from __future__ import annotations

from uuid import UUID

import httpx
from florada_payments.models.customer import Customer
from florada_payments.models.customer_list import CustomerList


class CustomersResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_customers(
        self,
        email: str | None = None,
        limit: int | None = 20,
        cursor: str | None = None,
    ) -> CustomerList:
        """List customers

        Args:
            email: email
            limit: limit
            cursor: cursor
        """
        url = "/customers"
        response = self._client.request(
            "GET",
            url,
            params={
                "email": email,
                "limit": limit,
                "cursor": cursor,
            },
        )
        response.raise_for_status()
        return CustomerList.model_validate(response.json())

    def create_customer(
        self,
    ) -> Customer:
        """Create a customer"""
        url = "/customers"
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return Customer.model_validate(response.json())

    def get_customer(
        self,
        customer_id: UUID,
    ) -> Customer:
        """Retrieve a customer

        Args:
            customer_id: Unique customer identifier
        """
        url = f"/customers/{customer_id}"
        response = self._client.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return Customer.model_validate(response.json())

    def update_customer(
        self,
        customer_id: UUID,
    ) -> Customer:
        """Update a customer

        Replaces all customer fields.

        Args:
            customer_id: Unique customer identifier
        """
        url = f"/customers/{customer_id}"
        response = self._client.request(
            "PUT",
            url,
        )
        response.raise_for_status()
        return Customer.model_validate(response.json())

    def delete_customer(
        self,
        customer_id: UUID,
    ) -> None:
        """Delete a customer

        Permanently deletes a customer and all associated data. Active
        subscriptions will be cancelled.

        Args:
            customer_id: Unique customer identifier
        """
        url = f"/customers/{customer_id}"
        response = self._client.request(
            "DELETE",
            url,
        )
        response.raise_for_status()

    def patch_customer(
        self,
        customer_id: UUID,
    ) -> Customer:
        """Partially update a customer

        Args:
            customer_id: Unique customer identifier
        """
        url = f"/customers/{customer_id}"
        response = self._client.request(
            "PATCH",
            url,
        )
        response.raise_for_status()
        return Customer.model_validate(response.json())
