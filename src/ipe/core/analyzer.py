from __future__ import annotations

from datetime import datetime, timezone

from ipe import __version__
from ipe.core.config import IpeConfig
from ipe.models.blueprint import APIBlueprint
from ipe.models.standard import AuthScheme, StandardModel, StandardOperation
from ipe.parsers.fetcher import fetch_spec
from ipe.parsers.models import OpenAPISpec, Operation
from ipe.parsers.openapi import parse_openapi

_HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")


class SpecAnalyzer:
    def parse(self, spec_path: str) -> OpenAPISpec:
        raw = fetch_spec(spec_path)
        return parse_openapi(raw)

    def extract(self, spec: OpenAPISpec, config: IpeConfig) -> APIBlueprint:
        operations = self._extract_operations(spec)
        models = self._extract_models(spec)
        auth_schemes = self._extract_auth_schemes(spec)
        server_urls = [s.url for s in spec.servers] if spec.servers else []

        return APIBlueprint(
            api_name=spec.info.title,
            spec_version=spec.info.version,
            spec_description=spec.info.description,
            base_url=server_urls[0] if server_urls else None,
            server_urls=server_urls,
            operations=operations,
            models=models,
            auth_schemes=auth_schemes,
            resources=_build_resources(operations),
            module_name=config.module_name or _derive_module_name(spec.info.title),
            generated_at=datetime.now(tz=timezone.utc).isoformat(),
            ipe_version=__version__,
            generator_config=config.targets.get(config.target, {}),
        )

    def _extract_operations(self, spec: OpenAPISpec) -> list[StandardOperation]:
        if not spec.paths:
            return []

        result: list[StandardOperation] = []
        for path, path_item in spec.paths.items():
            for method in _HTTP_METHODS:
                operation: Operation | None = getattr(path_item, method, None)
                if operation is not None:
                    result.append(
                        StandardOperation.from_operation(
                            path, method, operation, path_item
                        )
                    )
        return result

    def _extract_models(self, spec: OpenAPISpec) -> list[StandardModel]:
        if not spec.components or not spec.components.schemas:
            return []

        result: list[StandardModel] = []
        for name, schema in spec.components.schemas.items():
            model = StandardModel.from_schema(name, schema)
            if model is not None:
                result.append(model)
        return result

    def _extract_auth_schemes(self, spec: OpenAPISpec) -> list[AuthScheme]:
        if not spec.components or not spec.components.security_schemes:
            return []

        return [
            AuthScheme.from_security_scheme(name, scheme)
            for name, scheme in spec.components.security_schemes.items()
        ]


def _build_resources(
    operations: list[StandardOperation],
) -> dict[str, list[StandardOperation]]:
    resources: dict[str, list[StandardOperation]] = {}
    for op in operations:
        resource = _resource_name(op)
        resources.setdefault(resource, []).append(op)
    return resources


def _resource_name(op: StandardOperation) -> str:
    if op.tags:
        return op.tags[0].lower()
    segments = [s for s in op.path.split("/") if s and not s.startswith("{")]
    return segments[0] if segments else "default"


def _derive_module_name(title: str) -> str:
    result = title.lower().replace(" ", "_").replace("-", "_")
    return "".join(c for c in result if c.isalnum() or c == "_").strip("_") or "api"
