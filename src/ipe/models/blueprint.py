from typing import Any

from pydantic import BaseModel, Field

from ipe.models.standard import AuthScheme, StandardModel, StandardOperation


class OutputFile(BaseModel):
    template: str
    output_path: str
    context: dict[str, Any]


class APIBlueprint(BaseModel):
    api_name: str
    spec_version: str
    spec_description: str | None
    base_url: str | None
    server_urls: list[str]

    operations: list[StandardOperation]
    models: list[StandardModel]
    auth_schemes: list[AuthScheme]

    module_name: str
    generated_at: str
    ipe_version: str
    generator_config: dict[str, Any] = Field(default_factory=dict)
