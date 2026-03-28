from pathlib import Path

from ipe.core.analyzer import SpecAnalyzer

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestSpecAnalyzerParse:
    def test_parse_petstore(self):
        analyzer = SpecAnalyzer()

        spec = analyzer.parse(str(FIXTURES_DIR / "petstore.yaml"))

        assert spec.openapi == "3.0.0"
        assert spec.info.model_dump(by_alias=True, exclude_unset=True) == {
            "title": "Swagger Petstore",
            "version": "1.0.0",
            "license": {"name": "MIT"},
        }
        assert spec.paths is not None
        assert set(spec.paths.keys()) == {"/pets", "/pets/{petId}"}

    def test_parse_museum(self):
        analyzer = SpecAnalyzer()

        spec = analyzer.parse(str(FIXTURES_DIR / "museum.yaml"))

        assert spec.openapi == "3.1.0"
        assert spec.info.title == "Redocly Museum API"
        assert spec.info.version == "1.2.1"
        assert spec.paths is not None
        assert "/museum-hours" in spec.paths
        assert "/special-events" in spec.paths

    def test_parse_resolves_refs(self):
        analyzer = SpecAnalyzer()

        spec = analyzer.parse(str(FIXTURES_DIR / "petstore.yaml"))

        assert spec.paths is not None
        get_op = spec.paths["/pets"].get
        assert get_op is not None
        assert get_op.responses is not None
        resp = get_op.responses["200"]
        assert resp.content is not None
        schema = resp.content["application/json"].schema_
        assert schema is not None
        assert schema.model_dump(by_alias=True, exclude_unset=True) == {
            "type": "array",
            "maxItems": 100,
            "items": {
                "type": "object",
                "required": ["id", "name"],
                "properties": {
                    "id": {"type": "integer", "format": "int64"},
                    "name": {"type": "string"},
                    "tag": {"type": "string"},
                },
            },
        }
