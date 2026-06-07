from collections.abc import Callable
from datetime import UTC, datetime

from ipe import __version__
from ipe.core.config import IpeConfig
from ipe.models.blueprint import APIBlueprint
from ipe.models.standard import AuthScheme, StandardModel, StandardOperation
from ipe.parsers.fetcher import fetch_spec
from ipe.parsers.models import OpenAPISpec, Operation, PathItem
from ipe.parsers.openapi import parse_openapi
from ipe.utils.naming import to_pascal_case, to_snake_case

_HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")


class SpecAnalyzer:
    def parse(
        self,
        spec_path: str,
        on_phase: Callable[[str], None] | None = None,
    ) -> OpenAPISpec:
        report = on_phase or (lambda _: None)

        report("Loading spec")
        raw = fetch_spec(spec_path)

        return parse_openapi(raw, on_phase=on_phase)

    def extract(self, spec: OpenAPISpec, config: IpeConfig) -> APIBlueprint:
        server_urls = [s.url for s in spec.servers] if spec.servers else []
        operations, body_schemas = self._operations_and_body_schemas(spec)

        return APIBlueprint(
            api_name=spec.info.title,
            spec_version=spec.info.version,
            spec_description=spec.info.description,
            base_url=server_urls[0] if server_urls else None,
            server_urls=server_urls,
            operations=operations,
            models=self._models(spec),
            body_schemas=body_schemas,
            auth_schemes=self._auth_schemes(spec),
            module_name=config.module_name or to_snake_case(spec.info.title),
            generated_at=datetime.now(tz=UTC).isoformat(),
            ipe_version=__version__,
            generator_config=config.targets.get(config.target, {}),
        )

    def _operations_and_body_schemas(
        self, spec: OpenAPISpec
    ) -> tuple[list[StandardOperation], list[StandardModel]]:
        if not spec.paths:
            return [], []

        operations: list[StandardOperation] = []
        body_schemas: list[StandardModel] = []

        for path, path_item in spec.paths.items():
            for method in _HTTP_METHODS:
                operation_spec: Operation | None = getattr(path_item, method, None)
                if operation_spec is None:
                    continue

                operation, body_schema = self._build_operation(
                    path, method, operation_spec, path_item
                )

                operations.append(operation)
                if body_schema is not None:
                    body_schemas.append(body_schema)

        return operations, body_schemas

    def _build_operation(
        self,
        path: str,
        method: str,
        operation_spec: Operation,
        path_item: PathItem,
    ) -> tuple[StandardOperation, StandardModel | None]:
        operation = StandardOperation.from_operation(
            path, method, operation_spec, path_item
        )

        body_schema = self._synthesize_body_schema(operation_spec, operation.operation_id)

        if body_schema is not None and operation.request_body is not None:
            operation.request_body.model_names = [body_schema.name]

        return operation, body_schema

    def _synthesize_body_schema(
        self,
        operation_spec: Operation,
        operation_id: str,
    ) -> StandardModel | None:
        body = operation_spec.request_body
        if body is None or not body.content:
            return None

        content_type = next(iter(body.content))
        schema = body.content[content_type].schema_

        if schema is None or schema.ref or not schema.properties:
            return None

        model_name = to_pascal_case(operation_id) + "Request"
        return StandardModel.from_schema(model_name, schema)

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
