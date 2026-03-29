"""Pets resource."""

from __future__ import annotations

from typing import Any

import httpx


class PetsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_pets(
        self,
        limit: int | None = None,
    ) -> Any:
        """List all pets"""
        url = "/pets"
        response = self._client.request(
            "GET",
            url,
            params={
                "limit": limit,
            },
        )
        response.raise_for_status()
        return response.json()

    def create_pets(
        self,
    ) -> Any:
        """Create a pet"""
        url = "/pets"
        response = self._client.request(
            "POST",
            url,
        )
        response.raise_for_status()
        return response.json()

    def show_pet_by_id(
        self,
        pet_id: str,
    ) -> Any:
        """Info for a specific pet"""
        url = f"/pets/{pet_id}"
        response = self._client.request(
            "GET",
            url,
        )
        response.raise_for_status()
        return response.json()

