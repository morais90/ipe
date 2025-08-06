"""Test version information."""

import ipe


def test_version():
    """Test that version is defined and follows semver pattern."""
    assert ipe.__version__ == "0.1.0"
    assert isinstance(ipe.__version__, str)

    # Basic semver pattern check
    parts = ipe.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
