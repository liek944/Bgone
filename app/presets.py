"""Platform presets for image resizing."""

from typing import Optional, TypedDict


class SizePreset(TypedDict):
    width: int
    height: int


# Preset definitions for common platforms
PRESETS: dict[str, Optional[SizePreset]] = {
    "Etsy": {"width": 2000, "height": 2000},
    "Fiverr Gig": {"width": 688, "height": 459},
    "Fiverr Banner": {"width": 2400, "height": 1200},
    "Pinterest": {"width": 1000, "height": 1500},
    "Custom": None,  # User-defined dimensions
}


def get_preset_names() -> list[str]:
    """Return list of preset names for UI dropdown."""
    return list(PRESETS.keys())


def get_preset_size(name: str) -> Optional[SizePreset]:
    """Get dimensions for a preset, or None for Custom."""
    return PRESETS.get(name)
