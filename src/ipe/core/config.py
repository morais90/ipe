"""Configuration management for Ipê."""

import json
import keyword
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

from ipe.core.formatter import FormatterConfig


class IpeConfig(BaseModel):
    """Configuration for Ipê code generation.

    Parameters
    ----------
    target : str
        The language target to use. Defaults to "python".
    output_dir : Path
        The directory where generated code will be written.
    module_name : str, optional
        The name of the generated module. Auto-detected from spec if omitted.
    spec_path : str
        Path or URL to the OpenAPI specification.
    targets : dict
        Target-specific configuration options.
    template_dir : Path, optional
        Custom template directory for overriding built-in templates (v0.2+).
    """

    target: str = Field(default="python", description="Language target")
    output_dir: Path = Field(
        default=Path("./output"), description="Output directory for generated code"
    )
    module_name: str | None = Field(
        default=None, description="Name of the generated module"
    )
    spec_path: str = Field(default="", description="Path to OpenAPI specification")
    targets: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Target-specific configuration"
    )
    template_dir: Path | None = Field(
        default=None, description="Custom template directory"
    )
    formatter: FormatterConfig | None = Field(
        default=None,
        description="Override the target's default formatter",
    )
    auto_format: bool = Field(
        default=True,
        description="Run a code formatter after generation",
    )

    @field_validator("module_name")
    @classmethod
    def validate_module_name(cls, v: str | None) -> str | None:
        """Validate module name is a valid Python identifier.

        Parameters
        ----------
        v : str or None
            The module name to validate.

        Returns
        -------
        str or None
            The validated module name.
        """
        if v is None:
            return None

        if not v.isidentifier():
            raise ValueError(
                f"Module name '{v}' contains invalid characters. "
                "Please use only letters, numbers, and underscores. "
                "The name must start with a letter or underscore."
            )

        if keyword.iskeyword(v):
            raise ValueError(
                f"Module name '{v}' is a Python keyword. "
                "Please choose a different name."
            )

        return v

    @field_validator("output_dir", mode="before")
    @classmethod
    def coerce_output_dir(cls, v: Any) -> Path:
        """Ensure output directory is a Path."""
        return Path(v)

    @field_validator("template_dir", mode="before")
    @classmethod
    def coerce_template_dir(cls, v: Any) -> Path | None:
        """Ensure template directory is a Path or None."""
        if v is None:
            return None
        return Path(v)


def load_config(config_path: Path) -> IpeConfig:
    """Load configuration from JSON file.

    Parameters
    ----------
    config_path : Path
        Path to the configuration file.

    Returns
    -------
    IpeConfig
        The loaded configuration.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.
    ValueError
        If the configuration file contains invalid JSON.
    pydantic.ValidationError
        If the configuration does not match the expected schema.
    """
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "Please create an 'ipe.json' file or run 'ipe init' to get started."
        )

    try:
        config_data = json.loads(config_path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid JSON in configuration file: {config_path}\n"
            f"Error at line {e.lineno}, column {e.colno}: {e.msg}\n"
            "Please check your JSON syntax."
        ) from e

    return IpeConfig.model_validate(config_data)


def resolve_config(
    config_path: Path,
    *,
    spec: str | None = None,
    output: Path | None = None,
    target: str | None = None,
    module_name: str | None = None,
) -> IpeConfig:
    """Resolve configuration from CLI overrides, ``ipe.json``, then defaults.

    Parameters
    ----------
    config_path : Path
        Path to the ``ipe.json`` file; used as the baseline when it exists.
    spec : str, optional
        CLI override for the spec path or URL.
    output : Path, optional
        CLI override for the output directory.
    target : str, optional
        CLI override for the language target.
    module_name : str, optional
        CLI override for the generated module name.

    Returns
    -------
    IpeConfig
        The merged configuration, with CLI overrides winning over the file,
        and the file winning over built-in defaults.
    """
    base = load_config(config_path) if config_path.exists() else IpeConfig()
    data = base.model_dump()

    overrides = {
        "spec_path": spec,
        "output_dir": output,
        "target": target,
        "module_name": module_name,
    }
    data.update({key: value for key, value in overrides.items() if value is not None})

    return IpeConfig.model_validate(data)


def create_default_config(
    spec_path: str = "",
    output_dir: str = "./output",
    module_name: str | None = None,
) -> IpeConfig:
    """Create a configuration with intelligent defaults.

    Parameters
    ----------
    spec_path : str
        Path to the OpenAPI specification.
    output_dir : str, optional
        The output directory. Defaults to "./output".
    module_name : str, optional
        The name of the module to generate.

    Returns
    -------
    IpeConfig
        A configuration with sensible defaults.
    """
    return IpeConfig(
        spec_path=spec_path,
        output_dir=Path(output_dir),
        module_name=module_name,
    )


def save_config(config: IpeConfig, config_path: Path) -> None:
    """Save configuration to JSON file.

    Parameters
    ----------
    config : IpeConfig
        The configuration to save.
    config_path : Path
        Path where the configuration will be saved.
    """
    config_data = config.model_dump(exclude_none=True, mode="json")
    config_path.write_text(json.dumps(config_data, indent=2) + "\n")
