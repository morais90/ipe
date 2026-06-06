"""Disputes resource."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import httpx


class DisputesResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_disputes(
        self,
        status: str | None = None,
    ) -> Any:
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
        return response.json()

    def get_dispute(
        self,
        dispute_id: UUID,
    ) -> Any:
        """Retrieve a dispute

        Args:
            dispute_id: dispute_id
        """
        url = "/disputes/{dispute_id}".format(
            dispute_id=dispute_id,
        )
        response = self._client.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return response.json()

