# Media Orchestrator

A command-line tool that batch-processes a folder of images and videos: compressing files without visible quality loss and renaming them based on embedded capture metadata.

## Features

### Compression
- **Images (JPEG)**: adaptive re-encoding via Pillow, no perceptible visual loss.
- **Videos (MP4)**: size reduction via FFmpeg (H.264, CRF 23), visually equivalent quality.

### Metadata-based renaming
- Reads embedded capture metadata via ExifTool.
- Renames files to `YYYY-MM-DD_HHMMSS` based on their actual capture date.

### Execution
- Multi-threaded processing (I/O-bound), configurable worker count.
- Files are processed in place — no redundant copies are created.
- Structured logging instead of console prints.

## Requirements

- Python 3.9+
- [FFmpeg](https://ffmpeg.org/) available on `PATH`
- [ExifTool](https://exiftool.org/) available on `PATH`
- Pillow

```bash
pip install Pillow
```

## Usage

```bash
python media_orchestrator.py <target_dir> [--workers N]
```

**Arguments:**

| Argument      | Description                                      | Default |
|---------------|---------------------------------------------------|---------|
| `target_dir`  | Path to the folder containing the media files.     | required |
| `--workers`   | Number of worker threads for parallel processing.  | 4       |

**Example:**

```bash
python media_orchestrator.py "D:\Media\ToProcess" --workers 6
```

## Technical notes

- Renaming files to match their embedded capture date prevents cloud services from misclassifying uploads by upload date instead of capture date.
- Video re-encoding uses `-c:a copy` to preserve the original audio stream without re-encoding.
- Each file is processed independently; a failure on one file is logged and does not interrupt the batch.

## License

Free and open to use, modify, and integrate without restriction.
