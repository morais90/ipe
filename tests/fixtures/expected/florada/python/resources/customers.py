"""Customers resource."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import httpx


class CustomersResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_customers(
        self,
        email: str | None = None,
        limit: int | None = 20,
        cursor: str | None = None,
    ) -> Any:
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
        return response.json()

    def create_customer(
        self,
    ) -> Any:
        """Create a customer"""
        url = "/customers"
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return response.json()

    def get_customer(
        self,
        customer_id: UUID,
    ) -> Any:
        """Retrieve a customer

        Args:
            customer_id: Unique customer identifier
        """
        url = "/customers/{customer_id}".format(
            customer_id=customer_id,
        )
        response = self._client.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return response.json()

    def update_customer(
        self,
        customer_id: UUID,
    ) -> Any:
        """Update a customer

        Replaces all customer fields.

        Args:
            customer_id: Unique customer identifier
        """
        url = "/customers/{customer_id}".format(
            customer_id=customer_id,
        )
        response = self._client.request(
            "PUT",
            url,
        )
        response.raise_for_status()
        return response.json()

    def delete_customer(
        self,
        customer_id: UUID,
    ) -> Any:
        """Delete a customer

        Permanently deletes a customer and all associated data. Active
subscriptions will be cancelled.

        Args:
            customer_id: Unique customer identifier
        """
        url = "/customers/{customer_id}".format(
            customer_id=customer_id,
        )
        response = self._client.request(
            "DELETE",
            url,
        )
        response.raise_for_status()
        return response.json()

    def patch_customer(
        self,
        customer_id: UUID,
    ) -> Any:
        """Partially update a customer

        Args:
            customer_id: Unique customer identifier
        """
        url = "/customers/{customer_id}".format(
            customer_id=customer_id,
        )
        response = self._client.request(
            "PATCH",
            url,
        )
        response.raise_for_status()
        return response.json()

