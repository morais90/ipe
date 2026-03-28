from typing import Any, Optional


class IpeError(Exception):
    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.suggestion = suggestion
        self.details = details or {}

        full_message = message
        if suggestion:
            full_message += f"\n\nSuggestion: {suggestion}"

        super().__init__(full_message)

    def __str__(self) -> str:
        return self.message


class ConfigurationError(IpeError):
    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        config_path: Optional[str] = None,
        field: Optional[str] = None,
    ) -> None:
        details: dict[str, Any] = {}
        if config_path:
            details["config_path"] = config_path
        if field:
            details["field"] = field

        super().__init__(message, suggestion, details)


class ValidationError(IpeError):
    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        location: Optional[str] = None,
        line_number: Optional[int] = None,
        validation_errors: Optional[list[str]] = None,
    ) -> None:
        details: dict[str, Any] = {}
        if location:
            details["location"] = location
        if line_number:
            details["line_number"] = line_number
        if validation_errors:
            details["validation_errors"] = validation_errors

        super().__init__(message, suggestion, details)


class GenerationError(IpeError):
    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        output_path: Optional[str] = None,
        template_name: Optional[str] = None,
        target: Optional[str] = None,
    ) -> None:
        details: dict[str, Any] = {}
        if output_path:
            details["output_path"] = output_path
        if template_name:
            details["template_name"] = template_name
        if target:
            details["target"] = target

        super().__init__(message, suggestion, details)


class NetworkError(IpeError):
    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ) -> None:
        details: dict[str, Any] = {}
        if url:
            details["url"] = url
        if status_code:
            details["status_code"] = status_code
        if response_text:
            details["response_text"] = response_text

        super().__init__(message, suggestion, details)


class UnsupportedFeatureError(IpeError):
    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        feature: Optional[str] = None,
        version: Optional[str] = None,
        required_version: Optional[str] = None,
    ) -> None:
        details: dict[str, Any] = {}
        if feature:
            details["feature"] = feature
        if version:
            details["version"] = version
        if required_version:
            details["required_version"] = required_version

        super().__init__(message, suggestion, details)


class TemplateError(IpeError):
    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        template_path: Optional[str] = None,
        error_line: Optional[int] = None,
        template_error: Optional[str] = None,
    ) -> None:
        details: dict[str, Any] = {}
        if template_path:
            details["template_path"] = template_path
        if error_line:
            details["error_line"] = error_line
        if template_error:
            details["template_error"] = template_error

        super().__init__(message, suggestion, details)
