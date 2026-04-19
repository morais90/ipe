"""DisputesEvidence resource."""

from __future__ import annotations

from typing import Any

import httpx


class DisputesEvidenceResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def submit_dispute_evidence(
        self,
        dispute_id: UUID,
    ) -> Any:
        """Submit dispute evidence

        Submit evidence to contest a dispute. Can only be submitted once while
dispute is open.

        Args:
            dispute_id: dispute_id
        """
        url = "/disputes/{dispute_id}/evidence".format(
            dispute_id=dispute_id,
        )
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return response.json()

