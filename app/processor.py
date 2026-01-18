"""Single image processing: remove background and export transparent PNG."""

from pathlib import Path

from PIL import Image
from rembg import remove

from app.config import SUPPORTED_FORMATS


def process_image(input_path: Path, output_path: Path) -> bool:
    """
    Remove background from an image and save as transparent PNG.
    
    Args:
        input_path: Path to the input image
        output_path: Path for the output transparent PNG
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ValueError: If input format is not supported
        FileNotFoundError: If input file doesn't exist
    """
    # Validate input exists
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Validate format
    suffix = input_path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {suffix}. Supported: {SUPPORTED_FORMATS}")
    
    # Load image
    with Image.open(input_path) as img:
        # Remove background (returns RGBA)
        result = remove(img)
        
        # Ensure RGBA mode
        if result.mode != "RGBA":
            result = result.convert("RGBA")
        
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as PNG with alpha channel
        result.save(output_path, format="PNG")
    
    return True
