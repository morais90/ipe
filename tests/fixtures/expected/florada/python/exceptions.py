"""Florada Payments API exceptions."""


class FloradaPaymentsError(Exception):
    """Base exception for Florada Payments API errors."""

    def __init__(self, message: str, status_code: int | None = None, response: object | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class BadRequestError(FloradaPaymentsError):
    pass


class UnauthorizedError(FloradaPaymentsError):
    pass


class ForbiddenError(FloradaPaymentsError):
    pass


class NotFoundError(FloradaPaymentsError):
    pass


class ConflictError(FloradaPaymentsError):
    pass


class ValidationError(FloradaPaymentsError):
    pass


class RateLimitError(FloradaPaymentsError):
    pass


class InternalServerError(FloradaPaymentsError):
    pass
