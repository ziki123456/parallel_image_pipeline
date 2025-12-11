# src/main.py
import queue
import threading
import multiprocessing

from pipeline.config import Config
from pipeline.loader import loader_thread
from pipeline.processor import processor_thread
from pipeline.saver import saver_thread
from pipeline.logger import log_info, log_error


def calculate_optimal_workers(num_images: int, config: Config) -> int:
    """
    Calculates optimal number of worker threads based on:
    - number of images
    - system CPU cores
    - max CPU cores allowed by config
    """
    system_cores = multiprocessing.cpu_count()
    allowed_cores = min(system_cores, config.max_cpu_cores)

    return max(1, min(num_images, allowed_cores))


def main() -> None:
    """
    Main entry point of the application.
    Handles:
    - configuration loading
    - automatic worker selection
    - thread initialization
    - program lifecycle logging
    """
    log_info("program_started")

    config = Config()

    raw_queue: queue.Queue = queue.Queue()
    processed_queue: queue.Queue = queue.Queue()

    # Start loader thread (loads file paths into the queue)
    loader = threading.Thread(
        target=loader_thread,
        args=(raw_queue, config),
        daemon=True,
        name="LoaderThread",
    )
    loader.start()
    loader.join()  # Wait until loader has finished listing images

    # Count number of discovered images
    num_images = raw_queue.qsize()
    log_info("images_discovered", count=num_images)

    # Determine worker count
    if config.auto_worker_mode:
        worker_count = calculate_optimal_workers(num_images, config)
    else:
        worker_count = config.num_workers

    system_cores = multiprocessing.cpu_count()

    log_info(
        "worker_selection",
        discovered_images=num_images,
        system_cpu_cores=system_cores,
        max_allowed_cores=config.max_cpu_cores,
        selected_workers=worker_count,
    )

    print(f"Detected images: {num_images}")
    print(f"System CPU cores: {system_cores}")
    print(f"Max allowed cores: {config.max_cpu_cores}")
    print(f"Worker threads selected: {worker_count}")

    # Shared worker counter used by the saver thread
    active_workers = {"count": worker_count}
    lock = threading.Lock()

    # Start worker threads
    workers: list[threading.Thread] = []
    for i in range(worker_count):
        t = threading.Thread(
            target=processor_thread,
            args=(i + 1, raw_queue, processed_queue, config, active_workers, lock),
            daemon=True,
            name=f"WorkerThread-{i + 1}",
        )
        workers.append(t)
        t.start()

    # Start saver thread
    saver = threading.Thread(
        target=saver_thread,
        args=(processed_queue, config, active_workers, lock),
        daemon=True,
        name="SaverThread",
    )
    saver.start()

    # Wait for all items in the queues to be processed
    raw_queue.join()
    processed_queue.join()

    # Wait for all worker threads
    for w in workers:
        w.join()

    # Wait for saver
    saver.join()

    log_info("program_finished")
    print("All tasks completed. Program finished.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error("program_crashed", error=str(e))
        raise
