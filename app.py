"""Main Gradio application for Stamp'd.

The UI exposes functionality for scanning stamps using a local Ollama
model, managing the gallery, exporting data and adjusting settings.  The
implementation focuses on being robust in a variety of environments – if
optional dependencies are missing the features gracefully degrade.
"""

from __future__ import annotations


import os
import shutil
import logging
from html import escape
from typing import List, Dict, Any
import gradio as gr
from werkzeug.utils import secure_filename

from ai_utils import generate_metadata
from db_utils import (
    init_db,
    insert_many,
    get_all_stamps,
    get_stamp,
    update_stamp,
)
from export_utils import export_csv, export_xlsx, export_pdf
from config import CONFIG, load_config, save_config, IMAGES_DIR, LOGS_DIR

# ---------------------------------------------------------------------------
# Logging and database initialisation
# ---------------------------------------------------------------------------
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "errors.log"),
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
)

init_db()

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------




def _scan_paths(paths: List[str], progress: gr.Progress | None = None) -> List[Dict[str, Any]]:
    """Scan *paths* and return metadata records."""
    records: List[Dict[str, Any]] = []
    total = len(paths)
    for idx, path in enumerate(paths, 1):
        try:
            md = generate_metadata(path)
        except Exception as exc:
            logging.error("scan failed for %s: %s", escape(path), escape(str(exc)))
            md = {"name": "", "country": "", "denomination": "", "description": ""}
        record = {
            "image_path": path,
            "stamp_name": md.get("name", ""),
            "country": md.get("country", ""),
            "denomination": md.get("denomination", ""),
            "description": md.get("description", ""),
        }
        records.append(record)
        if progress is not None:
            try:
                progress(idx / total)
            except Exception as e:
                logging.exception("Error updating progress: %s", e, exc_info=True)
    return records


def upload_and_scan(files: List[Any], progress: gr.Progress | None = None) -> List[Dict[str, Any]]:
    """Handle uploaded files and return scanned metadata."""
    paths = []
    for f in files:
        safe_filename = secure_filename(os.path.basename(f.name))
        dest = os.path.join(IMAGES_DIR, safe_filename)
        shutil.copy(f.name, dest)
        paths.append(dest)
    return _scan_paths(paths, progress)


def scan_and_sync_folder(progress: gr.Progress | None = None) -> List[Dict[str, Any]]:
    """Scan all images from ``IMAGES_DIR`` not yet in the database."""
    existing = {s.image_path for s in get_all_stamps()}
    paths = [
        os.path.join(IMAGES_DIR, f)
        for f in os.listdir(IMAGES_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg")) and os.path.join(IMAGES_DIR, f) not in existing
    ]
    return _scan_paths(paths, progress)




def save_scans(data: List[Dict[str, Any]]) -> str:
    try:
        insert_many(data)
        return "✅ Saved new stamps!"
    except Exception as e:
        logging.error(f"Save scans error: {str(e)}")
        return "❌ Error saving scans"

def refresh_gallery():
    return get_all_stamps()

def populate_details(stamp_id):
    return get_stamp_by_id(stamp_id)

def update_stamp_details(stamp_id, country, denomination, year, notes, catalog, mint_used):
    return update_stamp(stamp_id, country, denomination, year, notes, catalog, mint_used)

# === UI ===
with gr.Blocks(title="Stamp’d") as demo:
    gr.Markdown("# 📬 Stamp’d — Smart Stamp Cataloging")

    with gr.Tab("Scan"):
        upload = gr.File(file_count="multiple", file_types=["image"])
        with gr.Row():
            scan_btn = gr.Button("Upload and Scan")
            sync_btn = gr.Button("Scan and Sync Folder")
        scan_progress = gr.JSON(label="Scan Results")
        save_all = gr.Button("Save All")
        scan_status = gr.Textbox(label="Status")

        scan_btn.click(upload_and_scan, inputs=upload, outputs=scan_progress)
        sync_btn.click(scan_and_sync_folder, outputs=scan_progress)
        save_all.click(save_scans, inputs=scan_progress, outputs=scan_status)

    with gr.Tab("Gallery"):
        search = gr.Textbox(label="Search")
        gallery = gr.Dataframe(headers=["ID", "Image", "Name", "Country", "Denomination"], interactive=False)
        selected_id = gr.Number(label="Selected ID", precision=0)
        image = gr.Image(label="Stamp")
        name = gr.Textbox(label="Name")
        country = gr.Textbox(label="Country")
        denom = gr.Textbox(label="Denomination")
        desc = gr.Textbox(label="Description")
        year = gr.Textbox(label="Year")
        notes = gr.Textbox(label="Notes")
        catalog = gr.Textbox(label="Catalog Number")
        mint_used = gr.Textbox(label="Mint/Used")
        update_status = gr.Textbox(label="Update Result")
        edit_btn = gr.Button("Edit")
        save_btn = gr.Button("Save", visible=False)
        nav_prev = gr.Button("Previous")
        nav_next = gr.Button("Next")
        save_msg = gr.Textbox(label="Status")

        def refresh_gallery_cb(search_query):
            return load_gallery(search_query)

        search.submit(refresh_gallery_cb, inputs=search, outputs=gallery)
        demo.load(lambda: load_gallery(""), outputs=gallery)

        def gallery_select(evt: gr.SelectData):
            stamp_id = gallery.value[evt.index[0]][0]
            return populate_stamp(stamp_id)

        # Fix: Use gallery.select with correct input/output mapping
        # Assume populate_details returns all needed fields in order
        gallery.select(
            fn=populate_details,
            inputs=[selected_id],
            outputs=[selected_id, image, name, country, denom, desc]
        )

        update_btn = gr.Button("💾 Update Selected")
        update_btn.click(fn=update_stamp_details,
                         inputs=[selected_id, country, denom, year, notes, catalog, mint_used],
                         outputs=update_status)

        reverse_btn = gr.Button("🔍 Reverse Image Search")
        reverse_result = gr.HTML()

        reverse_btn.click(fn=reverse_image_lookup, inputs=[image], outputs=[reverse_result])

    with gr.Tab("📤 Export & Logs"):
        export_btn = gr.Button("Export CSV")
        export_msg = gr.Textbox()
        export_btn.click(fn=export_csv, outputs=export_msg)

        log_viewer = gr.File(label="Error Log")
        log_viewer.value = os.path.join(LOGS_DIR, "errors.log")

demo.launch(share=True)
