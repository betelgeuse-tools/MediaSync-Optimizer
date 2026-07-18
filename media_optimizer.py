"""
Media Orchestrator
-------------------
Batch-processes a folder of images and videos:
    1. Compresses files above a visual-loss threshold.
    2. Renames files based on embedded capture metadata (via ExifTool).
    3. Runs in place, using a thread pool for I/O-bound operations.

Requirements:
    - FFmpeg   (video compression)
    - ExifTool (metadata extraction / renaming)
    - Pillow   (image compression)
"""

import argparse
import logging
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_WORKERS = 4
JPEG_QUALITY = 85
VIDEO_CRF = "23"
VIDEO_PRESET = "veryfast"

IMAGE_EXTENSIONS = (".jpg", ".jpeg")
VIDEO_EXTENSIONS = (".mp4",)


def compress_image(file_path: Path) -> None:
    """Compress a JPEG image in place without visible quality loss."""
    with Image.open(file_path) as img:
        img.save(file_path, "JPEG", optimize=True, quality=JPEG_QUALITY)


def compress_video(file_path: Path) -> None:
    """Compress an MP4 video in place using H.264 at a visually lossless CRF."""
    temp_output = file_path.with_suffix(file_path.suffix + ".tmp.mp4")
    command = [
        "ffmpeg", "-y",
        "-i", str(file_path),
        "-c:v", "libx264",
        "-crf", VIDEO_CRF,
        "-preset", VIDEO_PRESET,
        "-c:a", "copy",
        str(temp_output),
    ]
    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW,
        check=True,
    )
    os.replace(temp_output, file_path)


def rename_from_metadata(file_path: Path) -> None:
    """Rename a file based on its embedded capture date via ExifTool."""
    command = [
        "exiftool", "-overwrite_original",
        "-d", "%Y-%m-%d_%H%M%S.%%e",
        "-filename<DateTimeOriginal",
        "-filename<CreateDate",
        str(file_path),
    ]
    subprocess.run(
        command,
        capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
        check=True,
    )


def process_file(file_path: Path) -> str:
    """
    Process a single file:
        1. Compress (if applicable).
        2. Rename according to its capture metadata.

    Returns a status string for logging purposes.
    """
    try:
        suffix = file_path.suffix.lower()

        if suffix in IMAGE_EXTENSIONS:
            compress_image(file_path)
        elif suffix in VIDEO_EXTENSIONS:
            compress_video(file_path)

        rename_from_metadata(file_path)

        return f"OK: {file_path.name}"
    except Exception as exc:
        return f"ERROR: {file_path.name} | {exc}"


def collect_files(target_dir: Path) -> list[Path]:
    """Return all files directly inside the target directory."""
    return [p for p in target_dir.iterdir() if p.is_file()]


def run(target_dir: Path, workers: int) -> None:
    files = collect_files(target_dir)
    logger.info("Processing %d file(s) with %d worker(s)...", len(files), workers)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(process_file, files))

    for result in results:
        logger.info(result)

    logger.info("Processing complete.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compress and rename media files based on embedded metadata."
    )
    parser.add_argument(
        "target_dir",
        type=Path,
        help="Path to the folder containing the media files to process.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Number of worker threads (default: {DEFAULT_WORKERS}).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.target_dir.is_dir():
        logger.error("Target directory does not exist: %s", args.target_dir)
        raise SystemExit(1)

    run(args.target_dir, args.workers)


if __name__ == "__main__":
    main()