"""CLI entry point for Bgone."""

import argparse
import sys
from pathlib import Path

from app.config import OUTPUT_DIR, DEFAULT_SUFFIX
from app.processor import process_image
from app.batch import process_folder, get_output_path


def cmd_single(args: argparse.Namespace) -> int:
    """Handle single image processing."""
    input_path = Path(args.file)
    output_dir = Path(args.out)
    
    output_path = get_output_path(input_path, output_dir, args.suffix)
    
    # Check if exists
    if output_path.exists() and not args.overwrite:
        if not args.quiet:
            print(f"Skipped (exists): {output_path}")
        return 0
    
    try:
        process_image(input_path, output_path)
        if not args.quiet:
            print(f"Processed: {input_path.name} → {output_path}")
        return 0
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        return 1


def cmd_batch(args: argparse.Namespace) -> int:
    """Handle batch folder processing."""
    input_dir = Path(args.folder)
    output_dir = Path(args.out)
    
    try:
        result = process_folder(
            input_dir,
            output_dir,
            suffix=args.suffix,
            overwrite=args.overwrite,
            quiet=args.quiet
        )
        
        if not args.quiet:
            print(f"\nDone: {result.processed} processed, {result.skipped} skipped, {result.failed} failed")
        
        return 0 if result.failed == 0 else 1
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="bgone",
        description="Remove image backgrounds and export transparent PNGs"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Single command
    single_parser = subparsers.add_parser("single", help="Process a single image")
    single_parser.add_argument("file", help="Input image file")
    single_parser.add_argument("--out", default=str(OUTPUT_DIR), help="Output directory")
    single_parser.add_argument("--suffix", default=DEFAULT_SUFFIX, help="Output filename suffix")
    single_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    single_parser.add_argument("--quiet", action="store_true", help="Suppress output")
    single_parser.set_defaults(func=cmd_single)
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Process all images in a folder")
    batch_parser.add_argument("folder", help="Input folder")
    batch_parser.add_argument("--out", default=str(OUTPUT_DIR), help="Output directory")
    batch_parser.add_argument("--suffix", default=DEFAULT_SUFFIX, help="Output filename suffix")
    batch_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    batch_parser.add_argument("--quiet", action="store_true", help="Suppress output")
    batch_parser.set_defaults(func=cmd_batch)
    
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
