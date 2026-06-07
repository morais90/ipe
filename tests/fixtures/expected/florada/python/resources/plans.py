from __future__ import annotations

import httpx
from florada_payments.exceptions import validated
from florada_payments.models.create_plan_request import CreatePlanRequest
from florada_payments.models.plan import Plan


class PlansResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    @validated
    def list_plans(
        self,
        active: bool | None = None,
    ) -> list[Plan]:
        """List plans

        Args:
            active: active
        """
        url = "/plans"
        response = self._client.request(
            "GET",
            url,
            params={
                "active": active,
            },
        )
        response.raise_for_status()
        return [Plan.model_validate(item) for item in response.json()]

    @validated
    def create_plan(
        self,
        body: CreatePlanRequest,
    ) -> Plan:
        """Create a plan"""
        url = "/plans"
        response = self._client.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return Plan.model_validate(response.json())
