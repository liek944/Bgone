Purpose:

Convert images to transparent PNGs locally, fast, offline, and repeatable.

CORE DECISION

Local-only

CLI-first

Batch-capable

No database

No cloud

Deterministic output

TECH STACK (LOCKED)
Language: Python 3.10+
Core Model: rembg (U²-Net)
Image Lib: Pillow
Optional UI: None (CLI only)
OS: macOS / Windows / Linux

DIRECTORY STRUCTURE
transparent-tool/
│
├─ app/
│ ├─ **init**.py
│ ├─ processor.py # image → transparent PNG logic
│ ├─ batch.py # folder-based processing
│ └─ config.py # paths, formats, options
│
├─ cli/
│ ├─ **init**.py
│ └─ main.py # CLI entry point
│
├─ input/ # raw images (ignored by git)
├─ output/ # transparent results
│
├─ requirements.txt
├─ .gitignore
└─ README.md

PROCESSING CONTRACT

Input

JPG / PNG / WEBP

Single file or folder

Output

PNG with alpha channel

Same filename by default

Optional suffix: \_transparent.png

CORE LOGIC (processor.py)

Responsibilities:

Load image

Remove background

Preserve subject edges

Export transparent PNG

Rules:

Never mutate original file

Always output RGBA

Fail fast on unsupported formats

BATCH LOGIC (batch.py)

Responsibilities:

Scan input folder

Skip already processed files

Process in sequence (no concurrency needed)

Log success / failure per file

CLI CONTRACT (main.py)

Command patterns:

python main.py single input.jpg
python main.py batch ./input

Flags:

--out ./output
--suffix \_transparent
--overwrite false

CONFIG (config.py)

Centralized:

INPUT_DIR
OUTPUT_DIR
SUPPORTED_FORMATS
DEFAULT_SUFFIX

No env vars. No secrets.

INSTALL & RUN
pip install -r requirements.txt
python cli/main.py batch ./input

FAILURE HANDLING

Invalid file → skip + log

Model error → stop execution

Existing output → skip unless overwrite enabled

NON-GOALS (IMPORTANT)

❌ No auth

❌ No API

❌ No web UI

❌ No training models

❌ No cloud storage

This tool exists to solve my problem, not impress anyone.

OPTIONAL EXTENSIONS (ONLY IF NEEDED)

--preview flag (open output image)

--size-limit (skip huge files)

--trim (auto-crop transparent edges)

--zip (export results as archive)

FINAL CHECK

If I can:

Drop 50 images in a folder

Run one command

Get clean transparent PNGs

Then the tool is done.
