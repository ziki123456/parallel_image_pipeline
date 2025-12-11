# src/pipeline/processor.py
from queue import Queue, Empty
from typing import Dict

from PIL import Image, UnidentifiedImageError

from pipeline.config import Config
from pipeline.logger import log_info, log_error


def processor_thread(
    worker_id: int,
    raw_queue: Queue,
    processed_queue: Queue,
    config: Config,
    active_workers: Dict[str, int],
    lock
) -> None:
    """
    Worker thread that processes images from raw_queue and pushes results into processed_queue.
    Logs start, completion, and errors of processing.
    """

    thread_name = f"Worker-{worker_id}"

    log_info("worker_started", worker_id=worker_id)

    while True:
        try:
            # Try getting an image path
            image_path = raw_queue.get(timeout=1)
        except Empty:
            # No more work → worker is done
            with lock:
                active_workers["count"] -= 1
                remaining = active_workers["count"]

            log_info(
                "worker_finished",
                worker_id=worker_id,
                remaining_workers=remaining
            )
            break

        log_info(
            "processing_started",
            worker_id=worker_id,
            file=str(image_path)
        )

        try:
            # Open image
            with Image.open(image_path) as img:
                # Convert grayscale if enabled
                if config.grayscale:
                    img = img.convert("L")

                # Resize
                img = img.resize(config.resize_to)

                # Convert result to RGB so it can be saved easily
                img = img.convert("RGB")

                # Save processed image temporarily in memory
                processed_queue.put((image_path.name, img))

                log_info(
                    "image_processed",
                    worker_id=worker_id,
                    file=image_path.name,
                    resize=str(config.resize_to),
                    grayscale=config.grayscale
                )

        except (UnidentifiedImageError, OSError) as e:
            log_error(
                "processing_error",
                worker_id=worker_id,
                file=str(image_path),
                error=str(e)
            )
        finally:
            raw_queue.task_done()
