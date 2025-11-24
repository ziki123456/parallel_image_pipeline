# src/pipeline/processor.py
import os
import queue
import threading
from typing import Dict, Tuple

from PIL import Image

from .config import Config


def process_image(path: str, config: Config) -> Tuple[str, Image.Image]:
    """
    Vykoná samotné zpracování obrázku:
    - otevření
    - změna velikosti
    - případný převod na černobílý obrázek
    Vrací název souboru a objekt obrázku.
    """
    img = Image.open(path)

    # změna velikosti
    if config.resize_to is not None:
        img = img.resize(config.resize_to)

    # grayscale
    if config.grayscale:
        img = img.convert("L")

    filename = os.path.basename(path)
    return filename, img


def processor_thread(
    worker_id: int,
    raw_queue: queue.Queue,
    processed_queue: queue.Queue,
    config: Config,
    active_workers: Dict[str, int],
    lock: threading.Lock,
) -> None:
    """
    Worker vlákno:
    - čte cesty k souborům z raw_queue
    - každý obrázek zpracuje
    - výsledek (název + obrázek) vloží do processed_queue

    Když dostane hodnotu None, skončí a sníží čítač aktivních workerů.
    """
    print(f"[WORKER {worker_id}] Start")

    while True:
        path = raw_queue.get()

        # sentinel = konec práce pro toto vlákno
        if path is None:
            raw_queue.task_done()
            print(f"[WORKER {worker_id}] Sentinel, končím.")

            # bezpečně snížíme počet aktivních workerů
            with lock:
                active_workers["count"] -= 1
                print(f"[WORKER {worker_id}] Active workers: {active_workers['count']}")
            break

        try:
            print(f"[WORKER {worker_id}] Zpracovávám: {path}")
            filename, img = process_image(path, config)
            processed_queue.put((filename, img))
        except Exception as e:
            print(f"[WORKER {worker_id}] CHYBA při zpracování {path}: {e}")
        finally:
            raw_queue.task_done()

    print(f"[WORKER {worker_id}] Hotovo.")
