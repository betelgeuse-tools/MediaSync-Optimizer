# MediaSync-Optimizer

A Python automation tool to clean, compress, and resync metadata for a photo/video library before uploading to a cloud service (Google Photos, OneDrive, etc.).

## Features

### Compression
- **Images (JPG/JPEG)**: adaptive encoding optimization via Pillow, with no perceptible visual loss.
- **Videos (MP4)**: significant size reduction via FFmpeg (H.264 codec, CRF 23), visually equivalent quality.

### Metadata and renaming
- Extracts real metadata (EXIF for photos, QuickTime/ISO for videos).
- Automatically renames files to `YYYY-MM-DD_HHMMSS` based on actual capture date.

### Processing
- Multi-threaded execution, optimized for I/O.
- Modifies files in place (no redundant copies).

## Requirements

```bash
# System tools (Windows / Winget)
winget install FFmpeg
winget install ExifTool

# Python dependency
pip install Pillow
```

## Usage

1. Clone or download the repository.
2. Set the target folder in the script:

```python
TARGET_FOLDER = r"C:\Path\To\Your\Folder"
```

3. Run the script:

```bash
python orchestrateur_media.py
```

## Technical notes

- Aligning the filename with the internal metadata prevents files from being misclassified by upload date in cloud services.
- The `-codec copy` option is used during lightweight injections to preserve audio without unnecessary re-encoding.

## License

Free and open to use, modify, and integrate without restriction.
