# src/main.py
import queue
import threading

from pipeline.config import Config
from pipeline.loader import loader_thread
from pipeline.processor import processor_thread
from pipeline.saver import saver_thread


def main() -> None:
    """
    Hlavní vstupní bod aplikace.

    - načte konfiguraci
    - vytvoří fronty
    - spustí vlákno loaderu
    - spustí N worker vláken
    - spustí saver vlákno
    - počká, než všechno doběhne
    """
    config = Config()

    raw_queue: queue.Queue = queue.Queue()
    processed_queue: queue.Queue = queue.Queue()

    # sdílený počet aktivních workerů,
    # uložený ve slovníku kvůli mutabilitě (aby se dala hodnota měnit z vláken)
    active_workers = {"count": config.num_workers}
    lock = threading.Lock()

    # vlákno loaderu
    loader = threading.Thread(
        target=loader_thread,
        args=(raw_queue, config),
        daemon=True,
        name="LoaderThread",
    )
    loader.start()

    # worker vlákna
    workers: list[threading.Thread] = []
    for i in range(config.num_workers):
        t = threading.Thread(
            target=processor_thread,
            args=(i + 1, raw_queue, processed_queue, config, active_workers, lock),
            daemon=True,
            name=f"WorkerThread-{i + 1}",
        )
        workers.append(t)
        t.start()

    # saver vlákno
    saver = threading.Thread(
        target=saver_thread,
        args=(processed_queue, config, active_workers, lock),
        daemon=True,
        name="SaverThread",
    )
    saver.start()

    # počkáme na dokončení loaderu
    loader.join()

    # počkáme, až se zpracují všechny položky ve frontách
    raw_queue.join()
    processed_queue.join()

    # počkáme na všechny workery
    for w in workers:
        w.join()

    # počkáme na saver
    saver.join()

    print("Vše hotovo. Program končí.")


if __name__ == "__main__":
    main()
