from ipe.targets.python import auth
from ipe.targets.python.target import PythonTarget

TARGET = PythonTarget()


class TestAuthParams:
    def test_single_credential(self):
        schemes = [{"name": "bearerAuth", "kind": "bearer"}]

        assert auth.auth_params(TARGET, schemes) == "bearer_auth: str | None = None,"

    def test_basic_expands_to_username_and_password(self):
        schemes = [{"name": "basicAuth", "kind": "basic"}]

        assert auth.auth_params(TARGET, schemes) == (
            "basic_auth_username: str | None = None,\n"
            "basic_auth_password: str | None = None,"
        )

    def test_multiple_credentials(self):
        schemes = [
            {"name": "bearerAuth", "kind": "bearer"},
            {"name": "apiKeyAuth", "kind": "apikey", "parameter_name": "X-Key"},
        ]

        assert auth.auth_params(TARGET, schemes) == (
            "bearer_auth: str | None = None,\napi_key_auth: str | None = None,"
        )

    def test_colliding_names_are_uniquified(self):
        schemes = [
            {"name": "apiKey", "kind": "apikey", "parameter_name": "X-A"},
            {"name": "api_key", "kind": "apikey", "parameter_name": "X-B"},
        ]

        assert auth.auth_params(TARGET, schemes) == (
            "api_key: str | None = None,\napi_key_2: str | None = None,"
        )

    def test_transitive_collision_is_resolved(self):
        schemes = [
            {"name": "apiKey", "kind": "apikey", "parameter_name": "A"},
            {"name": "api_key", "kind": "apikey", "parameter_name": "B"},
            {"name": "api_key_2", "kind": "apikey", "parameter_name": "C"},
        ]

        assert auth.auth_params(TARGET, schemes) == (
            "api_key: str | None = None,\n"
            "api_key_2: str | None = None,\n"
            "api_key_2_2: str | None = None,"
        )

    def test_reserved_client_param_is_avoided(self):
        schemes = [{"name": "timeout", "kind": "bearer"}]

        assert auth.auth_params(TARGET, schemes) == "timeout_2: str | None = None,"


class TestAuthCallKwargs:
    def test_basic_passes_both_parts(self):
        schemes = [{"name": "basicAuth", "kind": "basic"}]

        assert auth.auth_call_kwargs(TARGET, schemes) == (
            "basic_auth_username=basic_auth_username,\n"
            "basic_auth_password=basic_auth_password,"
        )


class TestAuthApply:
    def test_bearer(self):
        schemes = [{"name": "bearerAuth", "kind": "bearer"}]

        assert auth.auth_apply(TARGET, schemes) == (
            "if bearer_auth is not None:\n"
            '    headers["Authorization"] = f"Bearer {bearer_auth}"'
        )

    def test_oauth2_applies_as_bearer(self):
        schemes = [{"name": "oauth2", "kind": "oauth2"}]

        assert auth.auth_apply(TARGET, schemes) == (
            'if oauth2 is not None:\n    headers["Authorization"] = f"Bearer {oauth2}"'
        )

    def test_api_key_in_header(self):
        schemes = [
            {
                "name": "apiKeyAuth",
                "kind": "apikey",
                "parameter_name": "X-Key",
                "location": "header",
            }
        ]

        assert auth.auth_apply(TARGET, schemes) == (
            "if api_key_auth is not None:\n    headers['X-Key'] = api_key_auth"
        )

    def test_api_key_in_query(self):
        schemes = [
            {
                "name": "apiKeyAuth",
                "kind": "apikey",
                "parameter_name": "api_key",
                "location": "query",
            }
        ]

        assert auth.auth_apply(TARGET, schemes) == (
            "if api_key_auth is not None:\n    params['api_key'] = api_key_auth"
        )

    def test_api_key_in_cookie(self):
        schemes = [
            {
                "name": "sessionAuth",
                "kind": "apikey",
                "parameter_name": "session_id",
                "location": "cookie",
            }
        ]

        assert auth.auth_apply(TARGET, schemes) == (
            "if session_auth is not None:\n    cookies['session_id'] = session_auth"
        )

    def test_api_key_name_is_escaped(self):
        schemes = [
            {
                "name": "apiKeyAuth",
                "kind": "apikey",
                "parameter_name": 'X"] = evil',
                "location": "header",
            }
        ]

        assert auth.auth_apply(TARGET, schemes) == (
            "if api_key_auth is not None:\n    headers['X\"] = evil'] = api_key_auth"
        )

    def test_basic(self):
        schemes = [{"name": "basicAuth", "kind": "basic"}]

        assert auth.auth_apply(TARGET, schemes) == (
            "if basic_auth_username is not None and basic_auth_password is not None:\n"
            '    raw = f"{basic_auth_username}:{basic_auth_password}".encode()\n'
            '    headers["Authorization"] = "Basic " + b64encode(raw).decode()'
        )


class TestAuthImports:
    def test_basic_needs_b64encode(self):
        schemes = [{"name": "basicAuth", "kind": "basic"}]

        assert auth.auth_imports(TARGET, schemes) == "from base64 import b64encode"

    def test_no_imports_without_basic(self):
        schemes = [{"name": "bearerAuth", "kind": "bearer"}]

        assert auth.auth_imports(TARGET, schemes) == ""
