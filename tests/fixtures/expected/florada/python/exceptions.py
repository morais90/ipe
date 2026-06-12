from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any

from pydantic import ValidationError as _PydanticValidationError
from pydantic import validate_call


class FloradaPaymentsError(Exception):
    """Base exception for Florada Payments API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: object | None = None,
    ) -> None:
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
    """Raised when client-side or server-side input validation fails."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: object | None = None,
        status_code: int | None = None,
        response: object | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response=response)
        self.field = field
        self.value = value


class RateLimitError(FloradaPaymentsError):
    pass


class InternalServerError(FloradaPaymentsError):
    pass


_STATUS_EXCEPTIONS: dict[int, type[FloradaPaymentsError]] = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    422: ValidationError,
    429: RateLimitError,
}


def _exception_type(status_code: int) -> type[FloradaPaymentsError]:
    mapped = _STATUS_EXCEPTIONS.get(status_code)

    if mapped is not None:
        return mapped

    if status_code >= 500:
        return InternalServerError

    return FloradaPaymentsError


def error_for_status(
    status_code: int,
    message: str,
    response: object | None = None,
) -> FloradaPaymentsError:
    """Return the exception that best matches an HTTP error status.

    Parameters
    ----------
    status_code : int
        HTTP status code of the failed response.
    message : str
        Human-readable description of the failure.
    response : object, optional
        Transport response that triggered the error.

    Returns
    -------
    FloradaPaymentsError
        The most specific exception for ``status_code``.
    """
    exc_type = _exception_type(status_code)

    return exc_type(message, status_code=status_code, response=response)


def _as_validation_error(exc: _PydanticValidationError) -> ValidationError:
    err = exc.errors()[0]
    field = ".".join(str(part) for part in err["loc"]) or None
    return ValidationError(err["msg"], field=field, value=err.get("input"))


def validated[F: Callable[..., Any]](func: F) -> F:
    """Decorator that validates arguments via Pydantic and surfaces failures
    as ValidationError with minimal context.
    """
    inner = validate_call(func)

    if iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await inner(*args, **kwargs)
            except _PydanticValidationError as exc:
                raise _as_validation_error(exc) from exc

        return async_wrapper  # type: ignore[return-value]

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return inner(*args, **kwargs)
        except _PydanticValidationError as exc:
            raise _as_validation_error(exc) from exc

    return wrapper  # type: ignore[return-value]
