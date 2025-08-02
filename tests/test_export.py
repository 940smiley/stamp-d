import os
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
os.environ["STAMPD_DB_PATH"] = str(ROOT / "test_export.db")

from db_utils import init_db, insert_stamp, Session, Stamp
from export_utils import export_csv, export_xlsx, export_pdf


def setup_module(module):
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
