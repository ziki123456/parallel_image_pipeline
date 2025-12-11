# src/pipeline/config.py
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple
import yaml


@dataclass
class Config:
    """
    Konfigurace aplikace načítaná z externího souboru config.yaml.
    YAML může přepsat libovolnou hodnotu, ale pokud tam něco chybí,
    použije se výchozí hodnota z dataclass.
    """

    # Výchozí hodnoty (fallback)
    input_dir: str = "input_Images"
    output_dir: str = "output"
    num_workers: int = 3
    resize_to: Tuple[int, int] = (800, 800)
    grayscale: bool = True

    def __post_init__(self) -> None:
        """
        Po inicializaci načteme hodnoty z config.yaml a přepíšeme jimi výchozí hodnoty.
        Soubor se vždy hledá v kořeni projektu (vedle README.md).
        """
        # Najdeme kořen projektu – nadřazený adresář "src"
        project_root = Path(__file__).resolve().parents[2]
        config_path = project_root / "config.yaml"

        if not config_path.exists():
            raise FileNotFoundError(
                f"Konfigurační soubor {config_path} neexistuje. "
                f"Umísti config.yaml do kořenového adresáře projektu."
            )

        # Načtení YAML
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        # Přepíšeme pouze položky, které jsou v YAML
        self.input_dir = data.get("input_dir", self.input_dir)
        self.output_dir = data.get("output_dir", self.output_dir)
        self.num_workers = int(data.get("num_workers", self.num_workers))

        resize_val = data.get("resize_to", list(self.resize_to))
        if isinstance(resize_val, (list, tuple)) and len(resize_val) == 2:
            self.resize_to = (int(resize_val[0]), int(resize_val[1]))

        self.grayscale = bool(data.get("grayscale", self.grayscale))
