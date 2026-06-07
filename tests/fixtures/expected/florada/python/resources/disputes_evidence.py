from __future__ import annotations

from uuid import UUID

import httpx
from florada_payments.exceptions import validated
from florada_payments.models.dispute import Dispute
from florada_payments.models.dispute_evidence import DisputeEvidence


class DisputesEvidenceResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    @validated
    def submit_dispute_evidence(
        self,
        dispute_id: UUID,
        body: DisputeEvidence,
    ) -> Dispute:
        """Submit dispute evidence

        Submit evidence to contest a dispute. Can only be submitted once
        while dispute is open.

        Args:
            dispute_id: dispute_id
        """
        url = f"/disputes/{dispute_id}/evidence"
        response = self._client.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return Dispute.model_validate(response.json())
