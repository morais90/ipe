from __future__ import annotations

from ipe.parsers.fetcher import fetch_spec
from ipe.parsers.models import OpenAPISpec
from ipe.parsers.openapi import parse_openapi


class SpecAnalyzer:
    def parse(self, spec_path: str) -> OpenAPISpec:
        raw = fetch_spec(spec_path)
        return parse_openapi(raw)
