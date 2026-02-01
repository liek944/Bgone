"""Core image resizing logic with multiple aspect ratio modes."""

from pathlib import Path
from typing import Literal, Tuple

from PIL import Image

# Aspect ratio handling modes
ResizeMode = Literal["fit", "fill", "stretch"]


def resize_image(
    input_path: Path,
    output_path: Path,
    width: int,
    height: int,
    mode: ResizeMode = "fit",
    bg_color: Tuple[int, int, int, int] = (255, 255, 255, 0),
) -> bool:
    """
    Resize an image to target dimensions with specified aspect ratio handling.

    Args:
        input_path: Path to source image
        output_path: Path for output image
        width: Target width in pixels
        height: Target height in pixels
        mode: How to handle aspect ratio
            - "fit": Scale to fit within bounds, pad with bg_color
            - "fill": Scale and center-crop to fill exactly
            - "stretch": Distort to exact dimensions
        bg_color: RGBA tuple for padding background (default: transparent)

    Returns:
        True if successful, False otherwise
    """
    try:
        with Image.open(input_path) as img:
            # Convert to RGBA for consistent handling
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            if mode == "stretch":
                result = _resize_stretch(img, width, height)
            elif mode == "fill":
                result = _resize_fill(img, width, height)
            else:  # fit
                result = _resize_fit(img, width, height, bg_color)

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save as PNG to preserve transparency
            result.save(output_path, "PNG")
            return True

    except Exception as e:
        print(f"Error resizing {input_path}: {e}")
        return False


def _resize_stretch(img: Image.Image, width: int, height: int) -> Image.Image:
    """Resize by stretching/distorting to exact dimensions."""
    return img.resize((width, height), Image.Resampling.LANCZOS)


def _resize_fill(img: Image.Image, width: int, height: int) -> Image.Image:
    """Resize and center-crop to fill exact dimensions."""
    target_ratio = width / height
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Image is wider - scale by height, crop width
        new_height = height
        new_width = int(height * img_ratio)
    else:
        # Image is taller - scale by width, crop height
        new_width = width
        new_height = int(width / img_ratio)

    # Scale
    scaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Center crop
    left = (new_width - width) // 2
    top = (new_height - height) // 2
    return scaled.crop((left, top, left + width, top + height))


def _resize_fit(
    img: Image.Image,
    width: int,
    height: int,
    bg_color: Tuple[int, int, int, int],
) -> Image.Image:
    """Resize to fit within bounds, padding with background color."""
    target_ratio = width / height
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Image is wider - scale by width
        new_width = width
        new_height = int(width / img_ratio)
    else:
        # Image is taller - scale by height
        new_height = height
        new_width = int(height * img_ratio)

    # Scale
    scaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create canvas and paste centered
    canvas = Image.new("RGBA", (width, height), bg_color)
    paste_x = (width - new_width) // 2
    paste_y = (height - new_height) // 2
    canvas.paste(scaled, (paste_x, paste_y), scaled)

    return canvas


def generate_filename(
    prefix: str,
    index: int,
    preset_name: str,
    width: int,
    height: int,
) -> str:
    """
    Generate output filename based on naming pattern.

    Format: {prefix}-{index:03d}-{preset}-{width}x{height}.png
    Example: product-001-etsy-2000x2000.png
    """
    preset_slug = preset_name.lower().replace(" ", "-")
    return f"{prefix}-{index:03d}-{preset_slug}-{width}x{height}.png"
