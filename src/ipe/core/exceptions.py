from typing import Any


class IpeError(Exception):
    def __init__(
        self,
        message: str,
        suggestion: str | None = None,
        details: dict[str, Any] | None = None,
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
        suggestion: str | None = None,
        config_path: str | None = None,
        field: str | None = None,
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
        suggestion: str | None = None,
        location: str | None = None,
        line_number: int | None = None,
        validation_errors: list[str] | None = None,
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
        suggestion: str | None = None,
        output_path: str | None = None,
        template_name: str | None = None,
        target: str | None = None,
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
        suggestion: str | None = None,
        url: str | None = None,
        status_code: int | None = None,
        response_text: str | None = None,
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
        suggestion: str | None = None,
        feature: str | None = None,
        version: str | None = None,
        required_version: str | None = None,
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
        suggestion: str | None = None,
        template_path: str | None = None,
        error_line: int | None = None,
        template_error: str | None = None,
    ) -> None:
        details: dict[str, Any] = {}
        if template_path:
            details["template_path"] = template_path
        if error_line:
            details["error_line"] = error_line
        if template_error:
            details["template_error"] = template_error

        super().__init__(message, suggestion, details)


class FormatterError(IpeError):
    pass
