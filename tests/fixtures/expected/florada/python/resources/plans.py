"""Plans resource."""

from __future__ import annotations

from typing import Any

import httpx


class PlansResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_plans(
        self,
        active: bool | None = None,
    ) -> Any:
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
        return response.json()

    def create_plan(
        self,
    ) -> Any:
        """Create a plan"""
        url = "/plans"
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return response.json()

