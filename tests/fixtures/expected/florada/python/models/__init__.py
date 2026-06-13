from __future__ import annotations

from florada_payments.models.address import Address
from florada_payments.models.attach_payment_method_request import (
    AttachPaymentMethodRequest,
)
from florada_payments.models.billing_interval import BillingInterval
from florada_payments.models.boleto_details import BoletoDetails
from florada_payments.models.cancel_subscription_request import (
    CancelSubscriptionRequest,
)
from florada_payments.models.capture_charge_request import CaptureChargeRequest
from florada_payments.models.card_details import CardDetails
from florada_payments.models.charge import Charge
from florada_payments.models.charge_list import ChargeList
from florada_payments.models.charge_status import ChargeStatus
from florada_payments.models.create_charge_request import CreateChargeRequest
from florada_payments.models.create_customer_request import CreateCustomerRequest
from florada_payments.models.create_plan_request import CreatePlanRequest
from florada_payments.models.create_refund_request import CreateRefundRequest
from florada_payments.models.create_subscription_request import (
    CreateSubscriptionRequest,
)
from florada_payments.models.create_webhook_request import CreateWebhookRequest
from florada_payments.models.customer import Customer
from florada_payments.models.customer_list import CustomerList
from florada_payments.models.dispute import Dispute
from florada_payments.models.dispute_evidence import DisputeEvidence
from florada_payments.models.dispute_reason import DisputeReason
from florada_payments.models.dispute_status import DisputeStatus
from florada_payments.models.error import Error
from florada_payments.models.field_error import FieldError
from florada_payments.models.money import Money
from florada_payments.models.pagination_meta import PaginationMeta
from florada_payments.models.patch_customer_request import PatchCustomerRequest
from florada_payments.models.payment_method import PaymentMethod
from florada_payments.models.pix_details import PixDetails
from florada_payments.models.plan import Plan
from florada_payments.models.refund import Refund
from florada_payments.models.subscription import Subscription
from florada_payments.models.subscription_status import SubscriptionStatus
from florada_payments.models.update_customer_request import UpdateCustomerRequest
from florada_payments.models.validation_error_response import ValidationErrorResponse
from florada_payments.models.webhook_endpoint import WebhookEndpoint
from pydantic import BaseModel

__all__: list[str] = [
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
]

_NAMESPACE: dict[str, type[BaseModel]] = {
    "Address": Address,
    "AttachPaymentMethodRequest": AttachPaymentMethodRequest,
    "BillingInterval": BillingInterval,
    "BoletoDetails": BoletoDetails,
    "CancelSubscriptionRequest": CancelSubscriptionRequest,
    "CaptureChargeRequest": CaptureChargeRequest,
    "CardDetails": CardDetails,
    "Charge": Charge,
    "ChargeList": ChargeList,
    "ChargeStatus": ChargeStatus,
    "CreateChargeRequest": CreateChargeRequest,
    "CreateCustomerRequest": CreateCustomerRequest,
    "CreatePlanRequest": CreatePlanRequest,
    "CreateRefundRequest": CreateRefundRequest,
    "CreateSubscriptionRequest": CreateSubscriptionRequest,
    "CreateWebhookRequest": CreateWebhookRequest,
    "Customer": Customer,
    "CustomerList": CustomerList,
    "Dispute": Dispute,
    "DisputeEvidence": DisputeEvidence,
    "DisputeReason": DisputeReason,
    "DisputeStatus": DisputeStatus,
    "Error": Error,
    "FieldError": FieldError,
    "Money": Money,
    "PaginationMeta": PaginationMeta,
    "PatchCustomerRequest": PatchCustomerRequest,
    "PaymentMethod": PaymentMethod,
    "PixDetails": PixDetails,
    "Plan": Plan,
    "Refund": Refund,
    "Subscription": Subscription,
    "SubscriptionStatus": SubscriptionStatus,
    "UpdateCustomerRequest": UpdateCustomerRequest,
    "ValidationErrorResponse": ValidationErrorResponse,
    "WebhookEndpoint": WebhookEndpoint,
}

for _model in _NAMESPACE.values():
    _model.model_rebuild(_types_namespace=_NAMESPACE)
