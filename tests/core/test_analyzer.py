from pathlib import Path

import pytest

from ipe.core.analyzer import SpecAnalyzer
from ipe.core.config import IpeConfig
from ipe.models.blueprint import APIBlueprint

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def florada_blueprint() -> APIBlueprint:
    analyzer = SpecAnalyzer()
    spec = analyzer.parse(str(FIXTURES_DIR / "florada.yaml"))
    config = IpeConfig(spec_path=str(FIXTURES_DIR / "florada.yaml"))
    return analyzer.extract(spec, config)


class TestSpecAnalyzerParse:
    def test_parse_florada(self):
        analyzer = SpecAnalyzer()

        spec = analyzer.parse(str(FIXTURES_DIR / "florada.yaml"))

        assert spec.openapi == "3.1.0"
        assert spec.info.title == "Florada Payments"
        assert spec.paths is not None

    def test_parse_florada_v30(self):
        analyzer = SpecAnalyzer()

        spec = analyzer.parse(str(FIXTURES_DIR / "florada-v3.0.yaml"))

        assert spec.openapi == "3.0.3"
        assert spec.info.title == "Florada Payments"

    def test_refs_resolve_lazily(self):
        analyzer = SpecAnalyzer()

        spec = analyzer.parse(str(FIXTURES_DIR / "florada.yaml"))

        assert spec.components is not None
        assert spec.components.schemas is not None
        charge = spec.components.schemas["Charge"]
        assert charge.properties is not None
        status = charge.properties["status"]
        assert status.ref == "#/components/schemas/ChargeStatus"
        assert status.type == "string"


class TestSpecAnalyzerExtractOperations:
    def test_operation_ids(self, florada_blueprint: APIBlueprint):
        assert [op.operation_id for op in florada_blueprint.operations] == [
            "listCharges",
            "createCharge",
            "getCharge",
            "captureCharge",
            "listChargeRefunds",
            "createRefund",
            "listCustomers",
            "createCustomer",
            "getCustomer",
            "updateCustomer",
            "deleteCustomer",
            "patchCustomer",
            "listPaymentMethods",
            "attachPaymentMethod",
            "detachPaymentMethod",
            "listSubscriptions",
            "createSubscription",
            "cancelSubscription",
            "listPlans",
            "createPlan",
            "listDisputes",
            "getDispute",
            "submitDisputeEvidence",
            "listWebhooks",
            "createWebhook",
            "deleteWebhook",
        ]

    def test_http_methods(self, florada_blueprint: APIBlueprint):
        methods = {op.method for op in florada_blueprint.operations}
        assert methods == {"GET", "POST", "PUT", "PATCH", "DELETE"}

    def test_operation_with_query_params(self, florada_blueprint: APIBlueprint):
        list_charges = florada_blueprint.operations[0]
        assert list_charges.operation_id == "listCharges"
        assert [p.name for p in list_charges.parameters] == [
            "status",
            "customer_id",
            "created_after",
            "created_before",
            "limit",
            "cursor",
        ]

    def test_operation_with_param_details(self, florada_blueprint: APIBlueprint):
        list_charges = florada_blueprint.operations[0]
        assert list_charges.operation_id == "listCharges"
        assert list_charges.parameters[4].name == "limit"
        assert list_charges.parameters[4].schema_type == "integer"
        assert list_charges.parameters[4].schema_format == "int32"


class TestSpecAnalyzerExtractResponses:
    def test_direct_ref_response(self, florada_blueprint: APIBlueprint):
        get_charge = next(
            op for op in florada_blueprint.operations if op.operation_id == "getCharge"
        )
        success = next(r for r in get_charge.responses if r.status_code == "200")

        assert success.model_dump() == {
            "status_code": "200",
            "description": "Charge details",
            "content_type": "application/json",
            "model_names": ["Charge"],
            "is_list": False,
            "discriminator": None,
            "primitive_type": None,
        }

    def test_paginated_list_response(self, florada_blueprint: APIBlueprint):
        list_charges = florada_blueprint.operations[0]
        success = next(r for r in list_charges.responses if r.status_code == "200")

        assert success.model_dump() == {
            "status_code": "200",
            "description": "Paginated list of charges",
            "content_type": "application/json",
            "model_names": ["ChargeList"],
            "is_list": False,
            "discriminator": None,
            "primitive_type": None,
        }


class TestSpecAnalyzerExtractModels:
    def test_model_names(self, florada_blueprint: APIBlueprint):
        assert {m.name for m in florada_blueprint.models} == {
            "Address",
            "AttachPaymentMethodRequest",
            "BillingInterval",
            "BoletoDetails",
            "CancelSubscriptionRequest",
            "CaptureChargeRequest",
            "CardDetails",
            "Charge",
            "ChargeList",
            "ChargeStatus",
            "CreateChargeRequest",
            "CreateCustomerRequest",
            "CreatePlanRequest",
            "CreateRefundRequest",
            "CreateSubscriptionRequest",
            "CreateWebhookRequest",
            "Customer",
            "CustomerList",
            "Dispute",
            "DisputeEvidence",
            "DisputeReason",
            "DisputeStatus",
            "Error",
            "FieldError",
            "Money",
            "PaginationMeta",
            "PatchCustomerRequest",
            "PaymentMethod",
            "PixDetails",
            "Plan",
            "Refund",
            "Subscription",
            "SubscriptionStatus",
            "UpdateCustomerRequest",
            "ValidationErrorResponse",
            "WebhookEndpoint",
        }

    def test_money_model(self, florada_blueprint: APIBlueprint):
        money = next(m for m in florada_blueprint.models if m.name == "Money")
        assert money.model_dump() == {
            "name": "Money",
            "description": None,
            "properties": [
                {
                    "name": "amount",
                    "schema_type": "integer",
                    "description": "Amount in smallest currency unit (e.g., cents)",
                    "schema_format": None,
                    "required": True,
                    "nullable": False,
                    "default": None,
                    "enum_values": None,
                    "validation_rules": [
                        {"rule_type": "minimum", "value": 0.0},
                    ],
                    "model_names": [],
                    "is_list": False,
                    "discriminator": None,
                    "item_primitive": None,
                },
                {
                    "name": "currency",
                    "schema_type": "string",
                    "description": "ISO 4217 currency code",
                    "schema_format": None,
                    "required": True,
                    "nullable": False,
                    "default": None,
                    "enum_values": None,
                    "validation_rules": [
                        {"rule_type": "min_length", "value": 3},
                        {"rule_type": "max_length", "value": 3},
                        {"rule_type": "pattern", "value": "^[A-Z]{3}$"},
                    ],
                    "model_names": [],
                    "is_list": False,
                    "discriminator": None,
                    "item_primitive": None,
                },
            ],
            "required_fields": ["amount", "currency"],
            "validation_rules": [],
        }


class TestSpecAnalyzerExtractAuth:
    def test_auth_schemes(self, florada_blueprint: APIBlueprint):
        assert {s.name for s in florada_blueprint.auth_schemes} == {
            "bearerAuth",
            "apiKeyAuth",
            "oauth2",
        }

    def test_bearer_auth(self, florada_blueprint: APIBlueprint):
        bearer = next(
            s for s in florada_blueprint.auth_schemes if s.name == "bearerAuth"
        )
        assert bearer.model_dump() == {
            "name": "bearerAuth",
            "type": "http",
            "scheme": "bearer",
            "location": None,
            "header_name": "Authorization",
        }

    def test_api_key_auth(self, florada_blueprint: APIBlueprint):
        api_key = next(
            s for s in florada_blueprint.auth_schemes if s.name == "apiKeyAuth"
        )
        assert api_key.model_dump() == {
            "name": "apiKeyAuth",
            "type": "apiKey",
            "scheme": None,
            "location": "header",
            "header_name": "X-Florada-Key",
        }


class TestSpecAnalyzerExtractMeta:
    def test_blueprint_metadata(self, florada_blueprint: APIBlueprint):
        assert florada_blueprint.api_name == "Florada Payments"
        assert florada_blueprint.spec_version == "1.0.0"
        assert (
            florada_blueprint.spec_description
            == "Payment processing platform API. Accept payments, manage customers, subscriptions, and disputes."
        )
        assert florada_blueprint.base_url == "https://api.florada.dev/v1"
        assert florada_blueprint.server_urls == [
            "https://api.florada.dev/v1",
            "https://sandbox.florada.dev/v1",
        ]
        assert florada_blueprint.module_name == "florada_payments"
        assert florada_blueprint.ipe_version == "0.1.0"
