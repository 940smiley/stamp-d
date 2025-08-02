# config.py - Central configuration for Stamp'd

import os

BASE_DIR = r"G:/stamp-d"

# Paths
DB_PATH = os.path.join(BASE_DIR, "stampd.db")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
THUMBNAILS_DIR = os.path.join(BASE_DIR, "thumbnails")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

# Feature toggles
AUTO_SYNC = True
SILENT_MODE = False
DEFAULT_MODEL = "phi3"
USE_OLLAMA = True
USE_LM_STUDIO = True

# Marketplace config
MARKETPLACES = ["ebay", "colnect", "delcampe", "stampworld"]
