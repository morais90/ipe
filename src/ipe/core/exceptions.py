"""Exception hierarchy for Ipê with user-friendly messages."""

from typing import Any, Optional


class IpeError(Exception):
    """Base exception for all Ipê errors.

    Provides user-friendly error messages suitable for non-native English
    speakers with clear explanations and helpful suggestions.

    Parameters
    ----------
    message : str
        The main error message.
    suggestion : str, optional
        A helpful suggestion to resolve the error.
    details : dict, optional
        Additional error details for debugging.

    Examples
    --------
    >>> raise IpeError("Something went wrong", "Try again later")
    """

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize the base error with message and optional suggestion."""
        self.message = message
        self.suggestion = suggestion
        self.details = details or {}

        full_message = message
        if suggestion:
            full_message += f"\n\nSuggestion: {suggestion}"

        super().__init__(full_message)

    def __str__(self) -> str:
        """Return a user-friendly string representation of the error."""
        return self.message


class ConfigurationError(IpeError):
    """Configuration-related errors.

    Raised when there are issues with configuration files, validation,
    or missing required settings.

    Examples
    --------
    >>> raise ConfigurationError(
    ...     "Configuration file not found",
    ...     "Create an 'ipe.json' file or run 'ipe init'"
    ... )
    """

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        config_path: Optional[str] = None,
        field: Optional[str] = None,
    ) -> None:
        """Initialize configuration error with context."""
        details: dict[str, Any] = {}
        if config_path:
            details["config_path"] = config_path
        if field:
            details["field"] = field

        super().__init__(message, suggestion, details)


class ValidationError(IpeError):
    """OpenAPI specification validation errors.

    Raised when the provided OpenAPI specification is invalid or
    contains unsupported features.

    Examples
    --------
    >>> raise ValidationError(
    ...     "Missing required field 'info.title'",
    ...     "Add a title field to the info section",
    ...     location="$.info.title"
    ... )
    """

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        location: Optional[str] = None,
        line_number: Optional[int] = None,
        validation_errors: Optional[list[str]] = None,
    ) -> None:
        """Initialize validation error with location context."""
        details: dict[str, Any] = {}
        if location:
            details["location"] = location
        if line_number:
            details["line_number"] = line_number
        if validation_errors:
            details["validation_errors"] = validation_errors

        super().__init__(message, suggestion, details)


class GenerationError(IpeError):
    """Code generation errors.

    Raised when code generation fails due to template issues,
    file system problems, or unsupported OpenAPI features.

    Examples
    --------
    >>> raise GenerationError(
    ...     "Failed to write generated files",
    ...     "Check that the output directory is writable",
    ...     output_path="./generated"
    ... )
    """

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        output_path: Optional[str] = None,
        template_name: Optional[str] = None,
        target: Optional[str] = None,
    ) -> None:
        """Initialize generation error with context."""
        details: dict[str, Any] = {}
        if output_path:
            details["output_path"] = output_path
        if template_name:
            details["template_name"] = template_name
        if target:
            details["target"] = target

        super().__init__(message, suggestion, details)


class NetworkError(IpeError):
    """Network-related errors.

    Raised when there are issues fetching OpenAPI specifications
    from URLs, including connection failures and HTTP errors.

    Examples
    --------
    >>> raise NetworkError(
    ...     "Failed to download OpenAPI specification",
    ...     "Check your internet connection and verify the URL",
    ...     url="https://api.example.com/openapi.yaml",
    ...     status_code=404
    ... )
    """

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ) -> None:
        """Initialize network error with HTTP context."""
        details: dict[str, Any] = {}
        if url:
            details["url"] = url
        if status_code:
            details["status_code"] = status_code
        if response_text:
            details["response_text"] = response_text

        super().__init__(message, suggestion, details)


class UnsupportedFeatureError(IpeError):
    """Unsupported OpenAPI feature errors.

    Raised when the OpenAPI specification contains features that
    are not yet supported by Ipê.

    Examples
    --------
    >>> raise UnsupportedFeatureError(
    ...     "OpenAPI 2.0 (Swagger) is not supported",
    ...     "Please upgrade your specification to OpenAPI 3.0 or later",
    ...     feature="OpenAPI 2.0",
    ...     version="2.0"
    ... )
    """

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        feature: Optional[str] = None,
        version: Optional[str] = None,
        required_version: Optional[str] = None,
    ) -> None:
        """Initialize unsupported feature error with version context."""
        details: dict[str, Any] = {}
        if feature:
            details["feature"] = feature
        if version:
            details["version"] = version
        if required_version:
            details["required_version"] = required_version

        super().__init__(message, suggestion, details)


class TemplateError(IpeError):
    """Template processing errors.

    Raised when there are issues with Jinja2 templates or
    template plugin loading.

    Examples
    --------
    >>> raise TemplateError(
    ...     "Template syntax error in client.py.jinja",
    ...     "Check the template file for syntax errors",
    ...     template_path="./templates/python/client.py.jinja",
    ...     error_line=42
    ... )
    """

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        template_path: Optional[str] = None,
        error_line: Optional[int] = None,
        template_error: Optional[str] = None,
    ) -> None:
        """Initialize template error with template context."""
        details: dict[str, Any] = {}
        if template_path:
            details["template_path"] = template_path
        if error_line:
            details["error_line"] = error_line
        if template_error:
            details["template_error"] = template_error

        super().__init__(message, suggestion, details)
