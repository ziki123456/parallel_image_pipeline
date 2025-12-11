# src/pipeline/loader.py
import os
from pathlib import Path
from queue import Queue
from typing import Optional

from PIL import Image, UnidentifiedImageError

from pipeline.config import Config
from pipeline.logger import log_info, log_error


def loader_thread(raw_queue: Queue, config: Config) -> None:
    """
    Loads image file paths from the input directory and pushes them into raw_queue.
    Logs every discovered file and handles loading errors.
    """
    input_path = Path(config.input_dir)

    if not input_path.exists():
        log_error("input_directory_missing", path=str(input_path))
        return

    log_info("loader_started", input_directory=str(input_path))

    # Scan for images
    for file_name in os.listdir(input_path):
        file_path = input_path / file_name

        # Skip directories
        if file_path.is_dir():
            continue

        # Try to validate file as an image
        try:
            with Image.open(file_path) as img:
                img.verify()  # Validate file header
        except (UnidentifiedImageError, OSError):
            log_error(
                "image_invalid",
                file_name=file_name,
                path=str(file_path)
            )
            continue

        # Image is valid → push into queue
        raw_queue.put(file_path)
        log_info(
            "image_discovered",
            file_name=file_name,
            path=str(file_path)
        )

    log_info("loader_finished")
