from __future__ import annotations

from uuid import UUID

import httpx
from florada_payments.models.webhook_endpoint import WebhookEndpoint


class WebhooksResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_webhooks(
        self,
    ) -> list[WebhookEndpoint]:
        """List webhook endpoints"""
        url = "/webhooks"
        response = self._client.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return [WebhookEndpoint.model_validate(item) for item in response.json()]

    def create_webhook(
        self,
    ) -> WebhookEndpoint:
        """Create a webhook endpoint"""
        url = "/webhooks"
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return WebhookEndpoint.model_validate(response.json())

    def delete_webhook(
        self,
        webhook_id: UUID,
    ) -> None:
        """Delete a webhook endpoint

        Args:
            webhook_id: webhook_id
        """
        url = f"/webhooks/{webhook_id}"
        response = self._client.request(
            "DELETE",
            url,
        )
        response.raise_for_status()
        return None
