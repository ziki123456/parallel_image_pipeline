# src/pipeline/loader.py
import os
import queue
from .config import Config


def loader_thread(raw_queue: queue.Queue, config: Config) -> None:
    """
    Vlákno, které prochází složku s obrázky a vkládá jejich cesty do fronty.

    Na konci vloží do fronty tolik speciálních hodnot (None),
    kolik je worker vláken. Tyto "sentinely" workerům říkají:
    'už není co dělat, můžeš skončit'.
    """
    print("[LOADER] Start")

    if not os.path.isdir(config.input_dir):
        print(f"[LOADER] Vstupní složka neexistuje: {config.input_dir}")
        return

    for filename in os.listdir(config.input_dir):
        path = os.path.join(config.input_dir, filename)

        # přeskočíme pod-složky
        if not os.path.isfile(path):
            continue

        # jednoduchý filtr na typy souborů
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        print(f"[LOADER] Přidávám do fronty: {path}")
        raw_queue.put(path)

    # po vložení všech cest vložíme sentinely
    for _ in range(config.num_workers):
        raw_queue.put(None)

    print("[LOADER] Hotovo, všechny soubory ve frontě.")
