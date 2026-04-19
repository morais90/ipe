"""Webhooks resource."""

from __future__ import annotations

from typing import Any

import httpx


class WebhooksResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_webhooks(
        self,
    ) -> Any:
        """List webhook endpoints"""
        url = "/webhooks"
        response = self._client.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return response.json()

    def create_webhook(
        self,
    ) -> Any:
        """Create a webhook endpoint"""
        url = "/webhooks"
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return response.json()

    def delete_webhook(
        self,
        webhook_id: UUID,
    ) -> Any:
        """Delete a webhook endpoint

        Args:
            webhook_id: webhook_id
        """
        url = "/webhooks/{webhook_id}".format(
            webhook_id=webhook_id,
        )
        response = self._client.request(
            "DELETE",
            url,
        )
        response.raise_for_status()
        return response.json()

