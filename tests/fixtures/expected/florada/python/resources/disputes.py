from __future__ import annotations

from typing import Literal
from uuid import UUID

from florada_payments.exceptions import validated
from florada_payments.models.dispute import Dispute
from florada_payments.transport import AsyncTransport, Transport


class DisputesResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    @validated
    def list_disputes(
        self,
        status: Literal["open", "under_review", "won", "lost"] | None = None,
    ) -> list[Dispute]:
        """List disputes

        Args:
            status: status
        """
        url = "/disputes"
        response = self._transport.request(
            "GET",
            url,
            params={
                "status": status,
            },
        )
        response.raise_for_status()
        return [Dispute.model_validate(item) for item in response.json()]

    @validated
    def get_dispute(
        self,
        dispute_id: UUID,
    ) -> Dispute:
        """Retrieve a dispute

        Args:
            dispute_id: dispute_id
        """
        url = f"/disputes/{dispute_id}"
        response = self._transport.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return Dispute.model_validate(response.json())


class AsyncDisputesResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @validated
    async def list_disputes(
        self,
        status: Literal["open", "under_review", "won", "lost"] | None = None,
    ) -> list[Dispute]:
        """List disputes

        Args:
            status: status
        """
        url = "/disputes"
        response = await self._transport.request(
            "GET",
            url,
            params={
                "status": status,
            },
        )
        response.raise_for_status()
        return [Dispute.model_validate(item) for item in response.json()]

    @validated
    async def get_dispute(
        self,
        dispute_id: UUID,
    ) -> Dispute:
        """Retrieve a dispute

        Args:
            dispute_id: dispute_id
        """
        url = f"/disputes/{dispute_id}"
        response = await self._transport.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return Dispute.model_validate(response.json())
