from __future__ import annotations

from uuid import UUID

import httpx
from florada_payments.models.dispute import Dispute


class DisputesResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_disputes(
        self,
        status: str | None = None,
    ) -> list[Dispute]:
        """List disputes

        Args:
            status: status
        """
        url = "/disputes"
        response = self._client.request(
            "GET",
            url,
            params={
                "status": status,
            },
        )
        response.raise_for_status()
        return [Dispute.model_validate(item) for item in response.json()]

    def get_dispute(
        self,
        dispute_id: UUID,
    ) -> Dispute:
        """Retrieve a dispute

        Args:
            dispute_id: dispute_id
        """
        url = f"/disputes/{dispute_id}"
        response = self._client.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return Dispute.model_validate(response.json())
