from typing import Any

import pytest
from pydantic import ValidationError

from ipe.parsers.models import Info, OpenAPISpec


class TestOpenAPISpecParsing:
    def test_florada_31(self, florada_spec: dict[str, Any]):
        spec = OpenAPISpec.model_validate(florada_spec)

        assert spec.openapi == "3.1.0"
        assert spec.info.title == "Florada Payments"
        assert spec.info.version == "1.0.0"
        assert spec.servers is not None
        assert [s.url for s in spec.servers] == [
            "https://api.florada.dev/v1",
            "https://sandbox.florada.dev/v1",
        ]
        assert spec.paths is not None
        assert set(spec.paths.keys()) == {
            "/charges",
            "/charges/{charge_id}",
            "/charges/{charge_id}/capture",
            "/charges/{charge_id}/refunds",
            "/customers",
            "/customers/{customer_id}",
            "/customers/{customer_id}/payment-methods",
            "/customers/{customer_id}/payment-methods/{method_id}",
            "/customers/{customer_id}/subscriptions",
            "/customers/{customer_id}/subscriptions/{subscription_id}/cancel",
            "/disputes",
            "/disputes/{dispute_id}",
            "/disputes/{dispute_id}/evidence",
            "/plans",
            "/webhooks",
            "/webhooks/{webhook_id}",
        }

    def test_florada_v30(self, florada_v30_spec: dict[str, Any]):
        spec = OpenAPISpec.model_validate(florada_v30_spec)

        assert spec.openapi == "3.0.3"
        assert spec.info.title == "Florada Payments"

    def test_florada_components(self, florada_spec: dict[str, Any]):
        spec = OpenAPISpec.model_validate(florada_spec)

        assert spec.components is not None
        assert spec.components.schemas is not None
        assert set(spec.components.schemas.keys()) == {
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
        assert spec.components.security_schemes is not None
        assert set(spec.components.security_schemes.keys()) == {
            "bearerAuth",
            "apiKeyAuth",
            "oauth2",
        }


class TestOpenAPISpecMinimal:
    def test_minimal_valid_spec(self):
        raw = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        spec = OpenAPISpec.model_validate(raw)

        assert spec.openapi == "3.0.0"
        assert spec.info.title == "Test"
        assert spec.paths == {}
        assert spec.components is None
        assert spec.servers is None

    def test_missing_openapi_raises(self):
        raw = {
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        with pytest.raises(ValidationError):
            OpenAPISpec.model_validate(raw)

    def test_missing_info_raises(self):
        raw = {
            "openapi": "3.0.0",
            "paths": {},
        }

        with pytest.raises(ValidationError):
            OpenAPISpec.model_validate(raw)


class TestInfoModel:
    def test_full_info(self):
        raw = {
            "title": "My API",
            "version": "2.0.0",
            "summary": "A summary",
            "description": "A description",
            "termsOfService": "https://example.com/tos",
            "contact": {"name": "Dev", "email": "dev@example.com"},
            "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        }

        info = Info.model_validate(raw)

        assert info.model_dump(by_alias=True, exclude_unset=True) == {
            "title": "My API",
            "version": "2.0.0",
            "summary": "A summary",
            "description": "A description",
            "termsOfService": "https://example.com/tos",
            "contact": {"name": "Dev", "email": "dev@example.com"},
            "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        }

    def test_minimal_info(self):
        raw = {"title": "API", "version": "1.0.0"}

        info = Info.model_validate(raw)

        assert info.model_dump(by_alias=True, exclude_unset=True) == {
            "title": "API",
            "version": "1.0.0",
        }
