# src/pipeline/saver.py
import os
import queue
import threading
from typing import Dict, Tuple

from PIL import Image

from .config import Config


def saver_thread(
    processed_queue: queue.Queue,
    config: Config,
    active_workers: Dict[str, int],
    lock: threading.Lock,
) -> None:
    """
    Vlákno, které ukládá zpracované obrázky z processed_queue do výstupní složky.

    Končí, když:
    - už nejsou aktivní workeři (active_workers["count"] == 0)
    A současně
    - fronta processed_queue je prázdná
    """
    print("[SAVER] Start")

    os.makedirs(config.output_dir, exist_ok=True)

    while True:
        try:
            # čeká max 0.5 sekundy na položku
            item: Tuple[str, Image.Image] = processed_queue.get(timeout=0.5)
        except queue.Empty:
            # když nic není, zkontrolujeme, jestli ještě někdo pracuje
            with lock:
                if active_workers["count"] == 0 and processed_queue.empty():
                    print("[SAVER] Žádní aktivní workeři a prázdná fronta, končím.")
                    break
            continue

        filename, img = item
        out_path = os.path.join(config.output_dir, filename)

        print(f"[SAVER] Ukládám: {out_path}")
        try:
            img.save(out_path)
        except Exception as e:
            print(f"[SAVER] CHYBA při ukládání {out_path}: {e}")
        finally:
            processed_queue.task_done()

    print("[SAVER] Hotovo.")
