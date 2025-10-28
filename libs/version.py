"""
Version management for HL-VOX-TimeLEFT.

Reads version from pyproject.toml to ensure single source of truth.
"""

from pathlib import Path
import re


def get_version() -> str:
    """
    Get application version from pyproject.toml.

    Returns:
        Version string (e.g., "0.1.0")
    """
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    try:
        with open(pyproject_path, "r") as f:
            content = f.read()

        # Extract version using regex
        match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        if match:
            return match.group(1)
        else:
            return "unknown"

    except FileNotFoundError:
        return "unknown"
    except Exception as e:
        print(f"Warning: Could not read version from pyproject.toml: {e}")
        return "unknown"


# Cache version for performance
__version__ = get_version()
