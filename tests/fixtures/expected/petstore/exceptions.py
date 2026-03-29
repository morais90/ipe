"""Swagger Petstore API exceptions."""


class SwaggerPetstoreError(Exception):
    """Base exception for Swagger Petstore API errors."""

    def __init__(self, message: str, status_code: int | None = None, response: object | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class BadRequestError(SwaggerPetstoreError):
    pass


class UnauthorizedError(SwaggerPetstoreError):
    pass


class ForbiddenError(SwaggerPetstoreError):
    pass


class NotFoundError(SwaggerPetstoreError):
    pass


class ConflictError(SwaggerPetstoreError):
    pass


class ValidationError(SwaggerPetstoreError):
    pass


class RateLimitError(SwaggerPetstoreError):
    pass


class InternalServerError(SwaggerPetstoreError):
    pass
