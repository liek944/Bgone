# Bgone

Local tool to remove image backgrounds and export transparent PNGs.

## Install

```bash
pip install -r requirements.txt
```

## GUI

Launch the graphical interface:

```bash
python -m gui.main
```

## CLI

### Single Image

```bash
python -m cli.main single image.jpg --out output/
```

### Batch Folder

```bash
python -m cli.main batch input/ --out output/
```

### Options

| Flag          | Description              | Default        |
| ------------- | ------------------------ | -------------- |
| `--out`       | Output directory         | `./output`     |
| `--suffix`    | Filename suffix          | `_transparent` |
| `--overwrite` | Overwrite existing files | `False`        |
| `--quiet`     | Suppress output          | `False`        |

## Supported Formats

- JPG / JPEG
- PNG
- WEBP
