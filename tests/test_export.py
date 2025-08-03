import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
os.environ["STAMPD_DB_PATH"] = str(ROOT / "test_export.db")

from db_utils import Session, Stamp, init_db, insert_stamp  # noqa: E402
from export_utils import export_csv, export_pdf, export_xlsx  # noqa: E402


def setup_module(module):
    db_path = os.environ["STAMPD_DB_PATH"]
    if os.path.exists(db_path):
        os.remove(db_path)
    init_db()
    session = Session()
    session.query(Stamp).delete()
    session.commit()
    insert_stamp({
        "image_path": str(ROOT / "images" / "sample_placeholder.jpg"),
        "stamp_name": "sample",
        "country": "Unknown",
        "denomination": "",
        "description": "test",
    })


def test_export_creates_files():
    csv_path = export_csv()
    xlsx_path = export_xlsx()
    pdf_path = export_pdf()
    assert os.path.exists(csv_path)
    assert os.path.exists(xlsx_path)
    assert os.path.exists(pdf_path)
