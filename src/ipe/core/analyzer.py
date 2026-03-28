from datetime import UTC, datetime

from ipe import __version__
from ipe.core.config import IpeConfig
from ipe.models.blueprint import APIBlueprint
from ipe.models.standard import AuthScheme, StandardModel, StandardOperation
from ipe.parsers.fetcher import fetch_spec
from ipe.parsers.models import OpenAPISpec, Operation
from ipe.parsers.openapi import parse_openapi
from ipe.utils.naming import to_snake_case

_HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")


class SpecAnalyzer:
    def parse(self, spec_path: str) -> OpenAPISpec:
        return parse_openapi(fetch_spec(spec_path))

    def extract(self, spec: OpenAPISpec, config: IpeConfig) -> APIBlueprint:
        server_urls = [s.url for s in spec.servers] if spec.servers else []

        return APIBlueprint(
            api_name=spec.info.title,
            spec_version=spec.info.version,
            spec_description=spec.info.description,
            base_url=server_urls[0] if server_urls else None,
            server_urls=server_urls,
            operations=self._operations(spec),
            models=self._models(spec),
            auth_schemes=self._auth_schemes(spec),
            module_name=config.module_name or to_snake_case(spec.info.title),
            generated_at=datetime.now(tz=UTC).isoformat(),
            ipe_version=__version__,
            generator_config=config.targets.get(config.target, {}),
        )

    def _operations(self, spec: OpenAPISpec) -> list[StandardOperation]:
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

    def _models(self, spec: OpenAPISpec) -> list[StandardModel]:
        if not spec.components or not spec.components.schemas:
            return []

        return [
            model
            for name, schema in spec.components.schemas.items()
            if (model := StandardModel.from_schema(name, schema)) is not None
        ]

    def _auth_schemes(self, spec: OpenAPISpec) -> list[AuthScheme]:
        if not spec.components or not spec.components.security_schemes:
            return []

        return [
            AuthScheme.from_security_scheme(name, scheme)
            for name, scheme in spec.components.security_schemes.items()
        ]
