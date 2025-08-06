"""Configuration management for Ipê."""

import json
import keyword
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class IpeConfig(BaseModel):
    """Configuration for Ipê code generation.

    Parameters
    ----------
    module_name : str
        The name of the generated module. Must be a valid Python identifier.
    generator : str, optional
        The target language generator to use. Defaults to "python".
    output_dir : str
        The directory where generated code will be written.
    spec_path : str, optional
        Path to the OpenAPI specification file.
    base_url : str, optional
        Base URL for the API client.

    Raises
    ------
    ValueError
        If module_name contains invalid characters for a Python module.
    """

    module_name: str = Field(..., description="Name of the generated module")
    generator: str = Field(default="python", description="Target language generator")
    output_dir: str = Field(..., description="Output directory for generated code")
    spec_path: Optional[str] = Field(
        default=None, description="Path to OpenAPI specification"
    )
    base_url: Optional[str] = Field(default=None, description="Base URL for API client")

    @field_validator("module_name")
    @classmethod
    def validate_module_name(cls, v: str) -> str:
        """Validate module name is a valid Python identifier.

        Parameters
        ----------
        v : str
            The module name to validate.

        Returns
        -------
        str
            The validated module name.

        Raises
        ------
        ValueError
            If the module name contains invalid characters or is a keyword.
        """
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

    @field_validator("output_dir")
    @classmethod
    def validate_output_dir(cls, v: str) -> str:
        """Ensure output directory is a valid path.

        Parameters
        ----------
        v : str
            The output directory path.

        Returns
        -------
        str
            The validated output directory path.
        """
        return str(Path(v))

    @model_validator(mode="after")
    def validate_paths(self) -> "IpeConfig":
        """Validate that paths are properly formatted."""
        if self.spec_path:
            self.spec_path = str(Path(self.spec_path))
        return self


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

    Examples
    --------
    >>> config_path = Path("ipe.json")
    >>> config = load_config(config_path)
    >>> print(config.module_name)
    my_api_client
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


def create_default_config(
    module_name: str,
    output_dir: str = "./generated",
    spec_path: Optional[str] = None,
) -> IpeConfig:
    """Create a configuration with intelligent defaults.

    Parameters
    ----------
    module_name : str
        The name of the module to generate.
    output_dir : str, optional
        The output directory. Defaults to "./generated".
    spec_path : str, optional
        Path to the OpenAPI specification.

    Returns
    -------
    IpeConfig
        A configuration with sensible defaults.

    Examples
    --------
    >>> config = create_default_config("petstore_client")
    >>> config.generator
    'python'
    """
    return IpeConfig(
        module_name=module_name,
        output_dir=output_dir,
        spec_path=spec_path,
    )


def save_config(config: IpeConfig, config_path: Path) -> None:
    """Save configuration to JSON file.

    Parameters
    ----------
    config : IpeConfig
        The configuration to save.
    config_path : Path
        Path where the configuration will be saved.

    Examples
    --------
    >>> config = create_default_config("my_api")
    >>> save_config(config, Path("ipe.json"))
    """
    config_data = config.model_dump(exclude_none=True)
    config_path.write_text(json.dumps(config_data, indent=2) + "\n")
