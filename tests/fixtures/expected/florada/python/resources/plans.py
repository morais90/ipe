from __future__ import annotations

from florada_payments.exceptions import validated
from florada_payments.models.create_plan_request import CreatePlanRequest
from florada_payments.models.plan import Plan
from florada_payments.transport import AsyncTransport, Transport


class PlansResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

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
        response = self._transport.request(
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
        response = self._transport.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return Plan.model_validate(response.json())


class AsyncPlansResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @validated
    async def list_plans(
        self,
        active: bool | None = None,
    ) -> list[Plan]:
        """List plans

        Args:
            active: active
        """
        url = "/plans"
        response = await self._transport.request(
            "GET",
            url,
            params={
                "active": active,
            },
        )
        response.raise_for_status()
        return [Plan.model_validate(item) for item in response.json()]

    @validated
    async def create_plan(
        self,
        body: CreatePlanRequest,
    ) -> Plan:
        """Create a plan"""
        url = "/plans"
        response = await self._transport.request(
            "POST",
            url,
            json=body.model_dump(mode="json"),
        )
        response.raise_for_status()
        return Plan.model_validate(response.json())
