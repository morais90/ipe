from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ipe.targets.base import LanguageTarget


class Credential:
    """Renders one OpenAPI security scheme into the generated client's auth."""

    def __init__(self, base: str) -> None:
        self.base = base

    @classmethod
    def from_scheme(cls, target: LanguageTarget, scheme: dict[str, Any]) -> Credential:
        """Build the credential for a security scheme.

        Parameters
        ----------
        target : LanguageTarget
            The active language target, used for naming.
        scheme : dict[str, Any]
            The serialized auth scheme.

        Returns
        -------
        Credential
            The credential subclass matching the scheme's kind.
        """
        base = target.naming.field_name(scheme["name"])
        kind = scheme["kind"]

        if kind == "apikey":
            return ApiKeyCredential(
                base, scheme["parameter_name"], scheme.get("location")
            )

        if kind == "basic":
            return BasicCredential(base)

        if kind == "oauth2_client_credentials":
            return OAuth2ClientCredentialsCredential(base, scheme["token_url"])

        return BearerCredential(base)

    def param_names(self) -> list[str]:
        """Return the client parameter names this credential contributes.

        Returns
        -------
        list[str]
            The generated parameter names.
        """
        return [self.base]

    def params(self) -> list[str]:
        """Return the typed parameter declarations for the client signature.

        Returns
        -------
        list[str]
            One ``name: type = default`` declaration per parameter.
        """
        return [f"{name}: str | None = None" for name in self.param_names()]

    def call_kwargs(self) -> list[str]:
        """Return the keyword arguments forwarding each parameter.

        Returns
        -------
        list[str]
            One ``name=name`` argument per parameter.
        """
        return [f"{name}={name}" for name in self.param_names()]

    def imports(self) -> set[str]:
        """Return the import lines this credential's generated code needs.

        Returns
        -------
        set[str]
            The import statements, empty when none are required.
        """
        return set()

    def apply(self) -> str:
        """Return the generated code that applies this credential.

        Returns
        -------
        str
            The generated statement block.

        Raises
        ------
        NotImplementedError
            Always, on the base class; subclasses provide the behavior.
        """
        raise NotImplementedError


class BearerCredential(Credential):
    def apply(self) -> str:
        """Return code applying the token as a Bearer ``Authorization`` header.

        Returns
        -------
        str
            The generated statement block.
        """
        return (
            f"if {self.base} is not None:\n"
            f'    headers["Authorization"] = f"Bearer {{{self.base}}}"'
        )


_LOCATION_DICT = {"header": "headers", "query": "params", "cookie": "cookies"}


class ApiKeyCredential(Credential):
    def __init__(self, base: str, parameter_name: str, location: str | None) -> None:
        super().__init__(base)
        self.parameter_name = parameter_name
        self.location = location

    def apply(self) -> str:
        """Return code placing the API key in the configured location.

        Returns
        -------
        str
            The generated statement block.
        """
        target_dict = _LOCATION_DICT.get(self.location or "header", "headers")
        return (
            f"if {self.base} is not None:\n"
            f"    {target_dict}[{self.parameter_name!r}] = {self.base}"
        )


class BasicCredential(Credential):
    def param_names(self) -> list[str]:
        """Return the username and password parameter names.

        Returns
        -------
        list[str]
            The generated parameter names.
        """
        return [f"{self.base}_username", f"{self.base}_password"]

    def imports(self) -> set[str]:
        """Return the imports needed to encode Basic credentials.

        Returns
        -------
        set[str]
            The required import statements.
        """
        return {"from base64 import b64encode"}

    def apply(self) -> str:
        """Return code applying Basic credentials as an ``Authorization`` header.

        Returns
        -------
        str
            The generated statement block.
        """
        username, password = self.param_names()
        return (
            f"if {username} is not None and {password} is not None:\n"
            f'    raw = f"{{{username}}}:{{{password}}}".encode()\n'
            f'    headers["Authorization"] = "Basic " + b64encode(raw).decode()'
        )


class OAuth2ClientCredentialsCredential(Credential):
    def __init__(self, base: str, token_url: str) -> None:
        super().__init__(base)
        self.token_url = token_url

    def param_names(self) -> list[str]:
        """Return the client id and secret parameter names.

        Returns
        -------
        list[str]
            The generated parameter names.
        """
        return [f"{self.base}_client_id", f"{self.base}_client_secret"]

    def apply(self) -> str:
        """Return code wiring an ``OAuth2ClientCredentials`` auth handler.

        Returns
        -------
        str
            The generated statement block.
        """
        client_id, client_secret = self.param_names()
        return (
            f"if {client_id} is not None and {client_secret} is not None:\n"
            f"    auth = OAuth2ClientCredentials("
            f"{self.token_url!r}, {client_id}, {client_secret})"
        )


def _credentials(
    target: LanguageTarget, schemes: list[dict[str, Any]]
) -> list[Credential]:
    credentials = [Credential.from_scheme(target, scheme) for scheme in schemes]
    _uniquify_bases(credentials)
    return credentials


_RESERVED_PARAMS = {"base_url", "timeout", "transport"}


def _uniquify_bases(credentials: list[Credential]) -> None:
    seen: set[str] = set(_RESERVED_PARAMS)

    for credential in credentials:
        original = credential.base
        suffix = 2

        while any(name in seen for name in credential.param_names()):
            credential.base = f"{original}_{suffix}"
            suffix += 1

        seen.update(credential.param_names())


def auth_params(target: LanguageTarget, schemes: list[dict[str, Any]]) -> str:
    """Render the auth parameters for the client constructor signature.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    schemes : list[dict[str, Any]]
        The serialized auth schemes.

    Returns
    -------
    str
        The joined parameter declarations, one per line.
    """
    return "\n".join(
        f"{param},"
        for credential in _credentials(target, schemes)
        for param in credential.params()
    )


def auth_call_kwargs(target: LanguageTarget, schemes: list[dict[str, Any]]) -> str:
    """Render the keyword arguments forwarding auth parameters.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    schemes : list[dict[str, Any]]
        The serialized auth schemes.

    Returns
    -------
    str
        The joined keyword arguments, one per line.
    """
    return "\n".join(
        f"{kwarg},"
        for credential in _credentials(target, schemes)
        for kwarg in credential.call_kwargs()
    )


def auth_apply(target: LanguageTarget, schemes: list[dict[str, Any]]) -> str:
    """Render the code that applies every credential.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    schemes : list[dict[str, Any]]
        The serialized auth schemes.

    Returns
    -------
    str
        The joined credential application blocks.
    """
    return "\n".join(credential.apply() for credential in _credentials(target, schemes))


def auth_imports(target: LanguageTarget, schemes: list[dict[str, Any]]) -> str:
    """Render the imports required by the generated auth code.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    schemes : list[dict[str, Any]]
        The serialized auth schemes.

    Returns
    -------
    str
        The joined import statements, sorted.
    """
    lines = {
        line
        for credential in _credentials(target, schemes)
        for line in credential.imports()
    }
    return "\n".join(sorted(lines))


def has_client_credentials(
    target: LanguageTarget, schemes: list[dict[str, Any]]
) -> bool:
    """Return whether any scheme uses the OAuth2 client-credentials flow.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    schemes : list[dict[str, Any]]
        The serialized auth schemes.

    Returns
    -------
    bool
        ``True`` when at least one client-credentials scheme is present.
    """
    return any(
        isinstance(credential, OAuth2ClientCredentialsCredential)
        for credential in _credentials(target, schemes)
    )
