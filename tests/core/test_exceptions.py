import pytest

from ipe.core.exceptions import (
    ConfigurationError,
    GenerationError,
    IpeError,
    NetworkError,
    TemplateError,
    UnsupportedFeatureError,
    ValidationError,
)


class TestIpeError:
    def test_basic_error(self):
        error = IpeError("Something went wrong")

        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.suggestion is None
        assert error.details == {}

    def test_error_with_suggestion(self):
        error = IpeError("Something went wrong", "Try again")

        assert str(error) == "Something went wrong"
        assert error.suggestion == "Try again"
        assert "Suggestion: Try again" in str(error.args[0])

    def test_error_with_details(self):
        error = IpeError("Test error", details={"key": "value", "number": 42})

        assert error.details == {"key": "value", "number": 42}

    def test_inherits_from_exception(self):
        error = IpeError("Test")

        assert isinstance(error, Exception)
        assert isinstance(error, IpeError)


class TestConfigurationError:
    def test_basic_error(self):
        error = ConfigurationError("Config file not found")

        assert isinstance(error, IpeError)
        assert str(error) == "Config file not found"

    def test_error_with_full_context(self):
        error = ConfigurationError(
            "Invalid JSON", "Check syntax", config_path="./ipe.json", field="target"
        )

        assert error.suggestion == "Check syntax"
        assert error.details == {"config_path": "./ipe.json", "field": "target"}


class TestValidationError:
    def test_basic_error(self):
        error = ValidationError("Invalid OpenAPI spec")

        assert isinstance(error, IpeError)
        assert str(error) == "Invalid OpenAPI spec"

    def test_error_with_location(self):
        error = ValidationError(
            "Missing field", "Add the field", location="$.info.title", line_number=42
        )

        assert error.suggestion == "Add the field"
        assert error.details == {"location": "$.info.title", "line_number": 42}

    def test_error_with_multiple_errors(self):
        validation_errors = ["Error 1", "Error 2", "Error 3"]
        error = ValidationError(
            "Multiple validation errors", validation_errors=validation_errors
        )

        assert error.details == {"validation_errors": validation_errors}


class TestGenerationError:
    def test_basic_error(self):
        error = GenerationError("Generation failed")

        assert isinstance(error, IpeError)
        assert str(error) == "Generation failed"

    def test_error_with_full_context(self):
        error = GenerationError(
            "Cannot write files",
            "Check permissions",
            output_path="./output",
            template_name="client.py.jinja",
            target="python",
        )

        assert error.suggestion == "Check permissions"
        assert error.details == {
            "output_path": "./output",
            "template_name": "client.py.jinja",
            "target": "python",
        }


class TestNetworkError:
    def test_basic_error(self):
        error = NetworkError("Connection failed")

        assert isinstance(error, IpeError)
        assert str(error) == "Connection failed"

    def test_error_with_http_context(self):
        error = NetworkError(
            "HTTP 404 Not Found",
            "Check the URL",
            url="https://api.example.com/openapi.yaml",
            status_code=404,
            response_text="Page not found",
        )

        assert error.suggestion == "Check the URL"
        assert error.details == {
            "url": "https://api.example.com/openapi.yaml",
            "status_code": 404,
            "response_text": "Page not found",
        }


class TestUnsupportedFeatureError:
    def test_basic_error(self):
        error = UnsupportedFeatureError("Feature not supported")

        assert isinstance(error, IpeError)
        assert str(error) == "Feature not supported"

    def test_error_with_version_context(self):
        error = UnsupportedFeatureError(
            "OpenAPI 2.0 not supported",
            "Upgrade to OpenAPI 3.0+",
            feature="Swagger 2.0",
            version="2.0",
            required_version="3.0+",
        )

        assert error.suggestion == "Upgrade to OpenAPI 3.0+"
        assert error.details == {
            "feature": "Swagger 2.0",
            "version": "2.0",
            "required_version": "3.0+",
        }


class TestTemplateError:
    def test_basic_error(self):
        error = TemplateError("Template error")

        assert isinstance(error, IpeError)
        assert str(error) == "Template error"

    def test_error_with_full_context(self):
        error = TemplateError(
            "Syntax error in template",
            "Fix the template syntax",
            template_path="./templates/client.py.jinja",
            error_line=25,
            template_error="Undefined variable 'foo'",
        )

        assert error.suggestion == "Fix the template syntax"
        assert error.details == {
            "template_path": "./templates/client.py.jinja",
            "error_line": 25,
            "template_error": "Undefined variable 'foo'",
        }


class TestExceptionHierarchy:
    def test_all_inherit_from_ipe_error(self):
        assert issubclass(ConfigurationError, IpeError)
        assert issubclass(ValidationError, IpeError)
        assert issubclass(GenerationError, IpeError)
        assert issubclass(NetworkError, IpeError)
        assert issubclass(UnsupportedFeatureError, IpeError)
        assert issubclass(TemplateError, IpeError)

    def test_base_class_catches_subclasses(self):
        with pytest.raises(IpeError):
            raise ConfigurationError("test")

        with pytest.raises(IpeError):
            raise ValidationError("test")

        with pytest.raises(IpeError):
            raise GenerationError("test")
