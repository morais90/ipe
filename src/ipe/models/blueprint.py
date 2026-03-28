from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ipe.models.standard import AuthScheme, StandardModel, StandardOperation


@dataclass
class OutputFile:
    template: str
    output_path: str
    context: dict[str, Any]


@dataclass
class APIBlueprint:
    api_name: str
    spec_version: str
    spec_description: str | None
    base_url: str | None
    server_urls: list[str]

    operations: list[StandardOperation]
    models: list[StandardModel]
    auth_schemes: list[AuthScheme]

    resources: dict[str, list[StandardOperation]]

    module_name: str
    generated_at: str
    ipe_version: str
    generator_config: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
