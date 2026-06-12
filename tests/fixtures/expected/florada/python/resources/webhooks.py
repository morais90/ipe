from __future__ import annotations

from uuid import UUID

from florada_payments.exceptions import validated
from florada_payments.models.create_webhook_request import CreateWebhookRequest
from florada_payments.models.webhook_endpoint import WebhookEndpoint
from florada_payments.transport import AsyncTransport, Transport


class WebhooksResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    @validated
    def list_webhooks(
        self,
    ) -> list[WebhookEndpoint]:
        """List webhook endpoints"""
        url = "/webhooks"
        response = self._transport.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return [WebhookEndpoint.model_validate(item) for item in response.json()]

    @validated
    def create_webhook(
        self,
        body: CreateWebhookRequest,
    ) -> WebhookEndpoint:
        """Create a webhook endpoint"""
        url = "/webhooks"
        response = self._transport.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return WebhookEndpoint.model_validate(response.json())

    @validated
    def delete_webhook(
        self,
        webhook_id: UUID,
    ) -> None:
        """Delete a webhook endpoint

        Args:
            webhook_id: webhook_id
        """
        url = f"/webhooks/{webhook_id}"
        response = self._transport.request(
            "DELETE",
            url,
        )
        response.raise_for_status()
        return None


class AsyncWebhooksResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @validated
    async def list_webhooks(
        self,
    ) -> list[WebhookEndpoint]:
        """List webhook endpoints"""
        url = "/webhooks"
        response = await self._transport.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return [WebhookEndpoint.model_validate(item) for item in response.json()]

    @validated
    async def create_webhook(
        self,
        body: CreateWebhookRequest,
    ) -> WebhookEndpoint:
        """Create a webhook endpoint"""
        url = "/webhooks"
        response = await self._transport.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return WebhookEndpoint.model_validate(response.json())

    @validated
    async def delete_webhook(
        self,
        webhook_id: UUID,
    ) -> None:
        """Delete a webhook endpoint

        Args:
            webhook_id: webhook_id
        """
        url = f"/webhooks/{webhook_id}"
        response = await self._transport.request(
            "DELETE",
            url,
        )
        response.raise_for_status()
        return None
