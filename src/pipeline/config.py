# src/pipeline/config.py
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Config:
    """
    Konfigurace celé aplikace.

    Tady můžeš jednoduše měnit chování programu:
    - složky s obrázky
    - počet vláken (workerů)
    - velikost výsledných obrázků
    - zda převádět na černobílou
    """
    input_dir: str = "input"          # složka se vstupními obrázky
    output_dir: str = "output"        # složka pro výstupní obrázky
    num_workers: int = 3              # kolik vláken bude obrázky zpracovávat
    resize_to: Tuple[int, int] = (800, 800)  # nová velikost obrázků
    grayscale: bool = True            # True = převod na černobílý obrázek
