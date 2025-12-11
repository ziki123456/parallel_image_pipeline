# src/pipeline/logger.py
from __future__ import annotations

import json
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


# Determine project root (same approach as in config.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "events.jsonl"

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class LogRecord:
    """
    Represents a single log event written as one JSON line.
    """
    timestamp: str
    level: str
    event: str
    thread: str
    data: Optional[Dict[str, Any]] = None


def _current_timestamp() -> str:
    """
    Returns current UTC time in ISO 8601 format with milliseconds.
    """
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def log_event(event: str, level: str = "INFO", **data: Any) -> None:
    """
    Append a JSON log record to the log file.

    Example:
        log_event("image_loaded", file_name="cat.png", path="input_Images/cat.png")
    """
    record = LogRecord(
        timestamp=_current_timestamp(),
        level=level.upper(),
        event=event,
        thread=threading.current_thread().name,
        data=data or None,
    )

    json_line = json.dumps(asdict(record), ensure_ascii=False)

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json_line + "\n")


def log_info(event: str, **data: Any) -> None:
    """
    Convenience wrapper for info-level logs.
    """
    log_event(event=event, level="INFO", **data)


def log_error(event: str, **data: Any) -> None:
    """
    Convenience wrapper for error-level logs.
    """
    log_event(event=event, level="ERROR", **data)
