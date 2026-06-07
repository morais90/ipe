"""Plans resource."""

from __future__ import annotations

from florada_payments.models.plan import Plan

import httpx


class PlansResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

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

    def create_plan(
        self,
    ) -> Plan:
        """Create a plan"""
        url = "/plans"
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return Plan.model_validate(response.json())

