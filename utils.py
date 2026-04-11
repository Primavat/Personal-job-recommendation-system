"""
utils.py — shared helpers
"""

import logging
import sys
from pathlib import Path


def setup_logging(log_file: Path | None = None):
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )

    # Suppress noisy third-party loggers
    for noisy in ("httpx", "httpcore", "gspread", "google", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def load_seen_ids(path: Path) -> set[str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return set()
    return set(path.read_text(encoding="utf-8").splitlines())


def save_seen_ids(path: Path, ids: set[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(sorted(ids)), encoding="utf-8")
