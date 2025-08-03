import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
os.environ["STAMPD_DB_PATH"] = str(ROOT / "test_scan.db")

from app import load_gallery, save_scans, scan_and_sync_folder  # noqa: E402
from db import Session, Stamp, init_db  # noqa: E402
from config import IMAGES_DIR  # noqa: E402


def setup_module(module):
    db_path = os.environ["STAMPD_DB_PATH"]
    if os.path.exists(db_path):
        os.remove(db_path)
    init_db()
    session = Session()
    session.query(Stamp).delete()
    session.commit()


def test_scan_and_save():
    # ensure there is at least one image to scan
    image = os.path.join(IMAGES_DIR, "sample_placeholder.jpg")
    assert os.path.exists(image)
    data = scan_and_sync_folder()
    assert isinstance(data, list)
    if data:  # may be empty if already scanned
        save_scans(data)
    session = Session()
    assert session.query(Stamp).count() > 0


def test_gallery_load():
    rows = load_gallery("")
    assert isinstance(rows, list)
