# src/pipeline/saver.py
from pathlib import Path
from queue import Queue, Empty
from typing import Dict

from PIL import Image

from pipeline.config import Config
from pipeline.logger import log_info, log_error


def saver_thread(
    processed_queue: Queue,
    config: Config,
    active_workers: Dict[str, int],
    lock
) -> None:
    """
    Saves processed images from processed_queue into the output directory.
    Logs saving attempts, errors, and final completion.
    """

    output_path = Path(config.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    log_info("saver_started", output_directory=str(output_path))

    while True:
        try:
            file_name, image = processed_queue.get(timeout=1)
        except Empty:
            # If no more items AND all workers are done → saver can finish
            with lock:
                if active_workers["count"] == 0:
                    break
            continue

        save_path = output_path / file_name

        log_info(
            "saving_started",
            file=file_name,
            output_path=str(save_path)
        )

        try:
            # Save image on disk
            image.save(save_path)

            log_info(
                "image_saved",
                file=file_name,
                output_path=str(save_path)
            )

        except Exception as e:
            log_error(
                "saving_error",
                file=file_name,
                output_path=str(save_path),
                error=str(e)
            )

        finally:
            processed_queue.task_done()

    log_info("saver_finished")
