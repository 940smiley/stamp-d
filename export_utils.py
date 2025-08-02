import config
import os
import csv
import zipfile
from datetime import datetime
from db_utils import Session, Stamp
from image_utils import generate_thumbnail
import pandas as pd
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from config import BACKUP_DIR, DB_PATH, IMAGES_DIR

EXPORT_FOLDER = "exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

def timestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# -------------------------
# CSV Export
# -------------------------
def export_csv(filename=None):
    """Export all stamps to CSV."""
    session = Session()
    stamps = session.query(Stamp).all()

    if not filename:
        filename = f"stampd_export_{timestamp()}.csv"
    filepath = os.path.join(EXPORT_FOLDER, filename)

    fields = [
        "id", "image_path", "stamp_name", "catalog_number", "country", "color",
        "denomination", "perforation", "format", "mint_used", "year", "description", "notes",
        "collection", "listed", "marketplace", "listing_url", "price", "sold", "lot_number",
        "listing_status", "created_at", "updated_at"
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fields)
        for s in stamps:
            writer.writerow([getattr(s, f) for f in fields])

    return filepath

# -------------------------
# XLSX Export with Thumbnails
# -------------------------
def export_xlsx(filename=None, include_thumbnails=True):
    """Export all stamps to XLSX with optional thumbnails."""
    session = Session()
    stamps = session.query(Stamp).all()

    if not filename:
        filename = f"stampd_export_{timestamp()}.xlsx"
    filepath = os.path.join(EXPORT_FOLDER, filename)

    wb = Workbook()
    ws = wb.active
    headers = [
        "Thumbnail", "ID", "Stamp Name", "Catalog #", "Country", "Color",
        "Denomination", "Perforation", "Format", "Mint/Used", "Year", "Description", "Notes",
        "Collection", "Listed", "Marketplace", "Listing URL", "Price", "Sold", "Lot #",
        "Listing Status", "Created", "Updated"
    ]
    ws.append(headers)

    for s in stamps:
        row = [
            "", s.id, s.stamp_name, s.catalog_number, s.country, s.color,
            s.denomination, s.perforation, s.format, s.mint_used, s.year,
            s.description, s.notes, s.collection, s.listed, s.marketplace,
            s.listing_url, s.price, s.sold, s.lot_number,
            s.listing_status, s.created_at, s.updated_at
        ]
        ws.append(row)

        # Optionally embed thumbnail
        if include_thumbnails and os.path.exists(s.image_path):
            try:
                img = XLImage(s.image_path)
                img.width = 64
                img.height = 64
                ws.add_image(img, f"A{ws.max_row}")
            except Exception:
                pass

    wb.save(filepath)
    return filepath

# -------------------------
# Auto Backup with ZIP
# -------------------------
def auto_backup():
    """Create a timestamped ZIP of CSV + XLSX exports for backup."""
    csv_path = export_csv()
    xlsx_path = export_xlsx()

    zip_name = f"stampd_backup_{timestamp()}.zip"
    zip_path = os.path.join(EXPORT_FOLDER, zip_name)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(csv_path, os.path.basename(csv_path))
        zf.write(xlsx_path, os.path.basename(xlsx_path))

    return zip_path

# -------------------------
# Batch Export by Filter
# -------------------------
def export_filtered(filter_field=None, filter_value=None, filename=None):
    """Export filtered stamps to CSV by a specific field."""
    session = Session()
    query = session.query(Stamp)
    if filter_field and filter_value:
        query = query.filter(getattr(Stamp, filter_field) == filter_value)
    stamps = query.all()

    if not filename:
        filename = f"stampd_export_{filter_field}_{filter_value}_{timestamp()}.csv"
    filepath = os.path.join(EXPORT_FOLDER, filename)

    fields = [
        "id", "image_path", "stamp_name", "catalog_number", "country", "color",
        "denomination", "perforation", "format", "mint_used", "year", "description", "notes",
        "collection", "listed", "marketplace", "listing_url", "price", "sold", "lot_number",
        "listing_status", "created_at", "updated_at"
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fields)
        for s in stamps:
            writer.writerow([getattr(s, f) for f in fields])

    return filepath
# -------------------------
# Unified Export (CSV + XLSX)
# -------------------------
def export_all():
    """
    Export all stamps to both CSV and XLSX and return summary.
    """
    csv_path = export_csv()
    xlsx_path = export_xlsx()
    return f"Exported: {csv_path} and {xlsx_path}"



# export_utils.py — Handles CSV and Excel exports for Stamp’d

import os
import csv
from datetime import datetime
from openpyxl import Workbook
from db_utils import Session, Stamp
from config import BACKUP_DIR, DB_PATH, IMAGES_DIR

def export_all(format="csv"):
    session = Session()
    stamps = session.query(Stamp).all()
    filename = f"stampd_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if format == "csv":
        filepath = os.path.join(BACKUP_DIR, filename + ".csv")
        with open(filepath, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Image Path", "Thumbnail", "Country", "Denomination",
                "Year", "Color", "Perforation", "Block Type", "Description",
                "Catalog Number", "Mint/Used", "Lot Number",
                "Listed", "Listing URL", "Price"
            ])
            for s in stamps:
                writer.writerow([
                    s.id, s.image_path, s.thumbnail_path, s.country, s.denomination,
                    s.year, s.color, s.perforation, s.block_type, s.description,
                    s.catalog_number, s.mint_used, s.lot_number,
                    s.listed, s.listing_url, s.price
                ])
        return filepath

    elif format == "xlsx":
        filepath = os.path.join(BACKUP_DIR, filename + ".xlsx")
        wb = Workbook()
        ws = wb.active
        ws.append([
            "ID", "Image Path", "Thumbnail", "Country", "Denomination",
            "Year", "Color", "Perforation", "Block Type", "Description",
            "Catalog Number", "Mint/Used", "Lot Number",
            "Listed", "Listing URL", "Price"
        ])
        for s in stamps:
            ws.append([
                s.id, s.image_path, s.thumbnail_path, s.country, s.denomination,
                s.year, s.color, s.perforation, s.block_type, s.description,
                s.catalog_number, s.mint_used, s.lot_number,
                s.listed, s.listing_url, s.price
            ])
        wb.save(filepath)
        return filepath

    else:
        raise ValueError("Unsupported export format")

def auto_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    export_all("csv")
 
