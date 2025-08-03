# openinterpreter_config_setup.py
# Run this in OpenInterpreter to restructure and validate the Stamp'd app

import os
import re
import time
import subprocess

BASE_DIR = r"G:\\stamp-d"
CONFIG_PATH = os.path.join(BASE_DIR, "config.py")
FILES_TO_PATCH = [
    "app.py", "ai_utils.py", "db_utils.py", "export_utils.py",
    "verify_and_launch_stampd.py", "gallery.py", "reverse_search.py"
]

CONFIG_TEMPLATE = '''
# config.py - Central configuration

BASE_DIR = r"G:/stamp-d"
DB_PATH = f"{BASE_DIR}/stampd.db"
IMAGES_DIR = f"{BASE_DIR}/images"
THUMBNAILS_DIR = f"{BASE_DIR}/thumbnails"
LOGS_DIR = f"{BASE_DIR}/logs"
BACKUP_DIR = f"{BASE_DIR}/backups"

AUTO_SYNC = True
SILENT_MODE = False
DEFAULT_MODEL = "phi3"
USE_OLLAMA = True
USE_LM_STUDIO = True
MARKETPLACES = ["ebay", "colnect", "delcampe", "stampworld"]
'''

PATCHES = {
    "app.py": [
        (r"DB_PATH ?= ?['\"]stampd.db['\"]", "from config import DB_PATH"),
        (r"images_dir ?= ?['\"]images['\"]", "from config import IMAGES_DIR")
    ],
    "db_utils.py": [
        (r"DB_PATH ?= ?['\"]stampd.db['\"]", "from config import DB_PATH")
    ],
    "export_utils.py": [
        (r"DB_PATH ?= ?['\"]stampd.db['\"]", "from config import DB_PATH")
    ]
    # Extend for more files
}

os.makedirs(BASE_DIR, exist_ok=True)
with open(CONFIG_PATH, "w") as f:
    f.write(CONFIG_TEMPLATE)

for file in FILES_TO_PATCH:
    path = os.path.join(BASE_DIR, file)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            contents = f.read()
        # Apply patches
        for pattern, replacement in PATCHES.get(file, []):
            contents = re.sub(pattern, replacement, contents)
        # Inject config import if missing
        if "from config import" not in contents:
            contents = "from config import *\n" + contents
        with open(path, "w", encoding="utf-8") as f:
            f.write(contents)

# Re-run validator
os.chdir(BASE_DIR)
print("Running validation loop...")
for i in range(3):
    print(f"Attempt {i+1}/3... Launching Stamp'd")
    p = subprocess.run(["python", "verify_and_launch_stampd.py"], capture_output=True, text=True)
    print(p.stdout)
    if "Traceback" not in p.stdout:
        print("✅ No major errors detected. App launched successfully.")
        break
    time.sleep(5)

print("🔁 Validation loop complete.")
