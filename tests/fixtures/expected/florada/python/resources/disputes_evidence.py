from __future__ import annotations

from uuid import UUID

from florada_payments.models.dispute import Dispute

import httpx


class DisputesEvidenceResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def submit_dispute_evidence(
        self,
        dispute_id: UUID,
    ) -> Dispute:
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
        return Dispute.model_validate(response.json())

