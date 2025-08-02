import os
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
os.environ["STAMPD_DB_PATH"] = str(ROOT / "test_scan.db")

from app import scan_and_sync_folder, save_scans, load_gallery
from db_utils import Session, Stamp, init_db
from config import IMAGES_DIR


def setup_module(module):
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
