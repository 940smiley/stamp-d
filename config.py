"""Configuration utilities for Stamp'd.

Settings are stored in a JSON file so that the application can reload
changes at runtime.  This module exposes helper functions to read and
update that file as well as common path constants used throughout the
project.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# Default configuration written when no config file exists yet.
DEFAULT_CONFIG: Dict[str, Any] = {
    "ai_model": "phi3",
    "export_options": {
        "csv": True,
        "xlsx": True,
        "pdf": True,
        "ebay": False,
        "hipstamp": False,
        "colnect": False,
        "stampworld": False,
    },
    "gallery": {"enable_search": True},
}


def load_config() -> Dict[str, Any]:
    """Load configuration from ``CONFIG_FILE``.  If the file does not
    exist, ``DEFAULT_CONFIG`` is written to disk and returned."""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg: Dict[str, Any]) -> None:
    """Persist *cfg* to ``CONFIG_FILE``."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


# Load configuration immediately for modules that simply need access to
# values without wanting to manage file IO themselves.  Call ``load_config``
# again if a refreshed copy is required.
CONFIG = load_config()

# Common paths --------------------------------------------------------------
DB_PATH = os.environ.get("STAMPD_DB_PATH", os.path.join(BASE_DIR, "stampd.db"))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
THUMBNAILS_DIR = os.path.join(BASE_DIR, "thumbnails")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

for path in (IMAGES_DIR, THUMBNAILS_DIR, LOGS_DIR, BACKUP_DIR):
    os.makedirs(path, exist_ok=True)
