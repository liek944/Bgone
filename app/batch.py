"""Batch processing: handle folders of images."""

from pathlib import Path
from typing import NamedTuple

from tqdm import tqdm

from app.config import SUPPORTED_FORMATS, OUTPUT_FORMAT
from app.processor import process_image


class BatchResult(NamedTuple):
    """Result of batch processing."""
    processed: int
    skipped: int
    failed: int
    errors: list[tuple[Path, str]]
    cancelled: bool = False


def get_output_path(
    input_file: Path,
    output_dir: Path,
    suffix: str = ""
) -> Path:
    """Generate output path for an input file."""
    stem = input_file.stem + suffix
    return output_dir / (stem + OUTPUT_FORMAT)


def process_folder(
    input_dir: Path,
    output_dir: Path,
    suffix: str = "",
    overwrite: bool = False,
    quiet: bool = False
) -> BatchResult:
    """
    Process all supported images in a folder.
    
    Args:
        input_dir: Directory containing input images
        output_dir: Directory for output PNGs
        suffix: Optional suffix for output filenames
        overwrite: If True, overwrite existing outputs
        quiet: If True, suppress progress bar
        
    Returns:
        BatchResult with counts and any errors
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all supported files
    files = [
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
    ]
    
    processed = 0
    skipped = 0
    failed = 0
    errors: list[tuple[Path, str]] = []
    
    # Process with progress bar
    iterator = files if quiet else tqdm(files, desc="Processing", unit="img")
    
    for input_file in iterator:
        output_path = get_output_path(input_file, output_dir, suffix)
        
        # Skip if exists and not overwriting
        if output_path.exists() and not overwrite:
            skipped += 1
            if not quiet:
                tqdm.write(f"Skipped (exists): {input_file.name}")
            continue
        
        try:
            process_image(input_file, output_path)
            processed += 1
            if not quiet:
                tqdm.write(f"Processed: {input_file.name} → {output_path.name}")
        except Exception as e:
            failed += 1
            errors.append((input_file, str(e)))
            if not quiet:
                tqdm.write(f"Failed: {input_file.name} - {e}")
    
    return BatchResult(processed, skipped, failed, errors)
