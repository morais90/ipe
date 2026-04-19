from pathlib import Path

import pytest

from ipe.core.analyzer import SpecAnalyzer
from ipe.core.config import IpeConfig
from ipe.models.standard import StandardOperation
from ipe.targets.python.target import PythonTarget

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


@pytest.fixture
def target() -> PythonTarget:
    return PythonTarget()


@pytest.fixture
def florada_operations() -> list[StandardOperation]:
    analyzer = SpecAnalyzer()
    spec = analyzer.parse(str(FIXTURES_DIR / "florada.yaml"))
    config = IpeConfig(spec_path=str(FIXTURES_DIR / "florada.yaml"))
    blueprint = analyzer.extract(spec, config)
    return blueprint.operations


class TestPythonTargetProperties:
    def test_name(self, target: PythonTarget):
        assert target.name == "python"

    def test_default_config(self, target: PythonTarget):
        assert target.get_default_config() == {
            "client_library": "httpx",
            "async_support": True,
        }


class TestPythonTargetResolveType:
    def test_parameter_types(self, target: PythonTarget, florada_operations: list[StandardOperation]):
        list_charges = florada_operations[0]
        limit_param = next(p for p in list_charges.parameters if p.name == "limit")

        assert target.resolve_type(limit_param.schema_type, limit_param.schema_format) == "int"

    def test_property_types(self, target: PythonTarget):
        analyzer = SpecAnalyzer()
        spec = analyzer.parse(str(FIXTURES_DIR / "florada.yaml"))
        config = IpeConfig(spec_path=str(FIXTURES_DIR / "florada.yaml"))
        blueprint = analyzer.extract(spec, config)
        money_model = next(m for m in blueprint.models if m.name == "Money")
        amount_prop = next(p for p in money_model.properties if p.name == "amount")
        currency_prop = next(p for p in money_model.properties if p.name == "currency")

        assert target.resolve_type(amount_prop.schema_type, amount_prop.schema_format) == "int"
        assert target.resolve_type(currency_prop.schema_type, currency_prop.schema_format) == "str"

    def test_unknown_type_returns_any(self, target: PythonTarget):
        assert target.resolve_type("unknown", None) == "Any"

    def test_unknown_format_falls_back_to_base_type(self, target: PythonTarget):
        assert target.resolve_type("string", "unknown-format") == "str"


class TestPythonTargetGroup:
    def test_groups_by_nested_path(self, target: PythonTarget, florada_operations: list[StandardOperation]):
        resources = target.group(florada_operations)

        assert set(resources.keys()) == {
            "charges",
            "charges.capture",
            "charges.refunds",
            "customers",
            "customers.payment-methods",
            "customers.subscriptions",
            "customers.subscriptions.cancel",
            "disputes",
            "disputes.evidence",
            "plans",
            "webhooks",
        }
