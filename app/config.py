"""Centralized configuration for Bgone."""

from pathlib import Path

# Directories
INPUT_DIR: Path = Path("input")
OUTPUT_DIR: Path = Path("output")

# Supported input formats
SUPPORTED_FORMATS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}

# Output settings
DEFAULT_SUFFIX: str = "_transparent"
OUTPUT_FORMAT: str = ".png"
