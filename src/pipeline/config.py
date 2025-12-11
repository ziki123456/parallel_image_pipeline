# src/pipeline/config.py
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple
import yaml


@dataclass
class Config:
    """
    Application configuration loaded from an external config.yaml file.
    YAML values override defaults. Defaults are used if keys are missing.
    """

    input_dir: str = "input_Images"
    output_dir: str = "output"
    num_workers: int = 3
    resize_to: Tuple[int, int] = (800, 800)
    grayscale: bool = True

    # NEW SETTINGS
    max_cpu_cores: int = 4
    auto_worker_mode: bool = True

    def __post_init__(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        config_path = project_root / "config.yaml"

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file {config_path} not found. "
                f"Place config.yaml in the project root directory."
            )

        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        # Overwrite attributes if present in YAML
        self.input_dir = data.get("input_dir", self.input_dir)
        self.output_dir = data.get("output_dir", self.output_dir)

        self.num_workers = int(data.get("num_workers", self.num_workers))

        resize_val = data.get("resize_to", list(self.resize_to))
        if isinstance(resize_val, (list, tuple)) and len(resize_val) == 2:
            self.resize_to = (int(resize_val[0]), int(resize_val[1]))

        self.grayscale = bool(data.get("grayscale", self.grayscale))

        # NEW CONFIG FIELDS
        self.max_cpu_cores = int(data.get("max_cpu_cores", self.max_cpu_cores))
        self.auto_worker_mode = bool(data.get("auto_worker_mode", self.auto_worker_mode))
