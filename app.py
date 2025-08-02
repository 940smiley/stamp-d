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
from typing import List, Dict, Any

import gradio as gr

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
    records = []
    total = len(paths)
    for idx, path in enumerate(paths, 1):
        try:
            md = generate_metadata(path)
        except Exception as exc:  # pragma: no cover - defensive
            logging.error("scan failed for %s: %s", path, exc)
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
            except Exception:
                pass
    return records


def upload_and_scan(files: List[Any], progress: gr.Progress | None = None) -> List[Dict[str, Any]]:
    """Handle uploaded files and return scanned metadata."""
    paths = []
    for f in files:
        dest = os.path.join(IMAGES_DIR, os.path.basename(f.name))
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
    insert_many(data)
    return f"Saved {len(data)} stamps"


def load_gallery(search: str = "") -> List[List[Any]]:
    stamps = get_all_stamps()
    rows = []
    for s in stamps:
        if search and search.lower() not in (s.country or "").lower():
            continue
        rows.append([s.id, s.image_path, s.stamp_name, s.country, s.denomination])
    return rows


def populate_stamp(stamp_id: int) -> List[Any]:
    s = get_stamp(stamp_id)
    if not s:
        return [stamp_id, None, "", "", "", ""]
    return [s.id, s.image_path, s.stamp_name, s.country, s.denomination, s.description]


def save_stamp_details(stamp_id, name, country, denomination, description):
    update_stamp(
        int(stamp_id),
        stamp_name=name,
        country=country,
        denomination=denomination,
        description=description,
    )
    return "Saved"


def read_errors() -> str:
    path = os.path.join(LOGS_DIR, "errors.log")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_settings(ai_model, csv, xlsx, pdf, ebay, hipstamp, colnect, stampworld):
    cfg = load_config()
    cfg["ai_model"] = ai_model
    cfg["export_options"] = {
        "csv": csv,
        "xlsx": xlsx,
        "pdf": pdf,
        "ebay": ebay,
        "hipstamp": hipstamp,
        "colnect": colnect,
        "stampworld": stampworld,
    }
    save_config(cfg)
    return "Settings saved"


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="Stamp'd") as demo:
    gr.Markdown("# 📬 Stamp'd — Smart Stamp Cataloging")

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

        gallery.select(gallery_select, outputs=[selected_id, image, name, country, denom, desc])

        def enter_edit_mode():
            return gr.update(visible=True), gr.update(visible=False)

        def save_current(stamp_id, name, country, denom, desc):
            msg = save_stamp_details(stamp_id, name, country, denom, desc)
            return (
                gr.update(visible=False),
                gr.update(visible=True),
                msg,
            )

        edit_btn.click(enter_edit_mode, outputs=[save_btn, edit_btn])
        save_btn.click(
            save_current,
            inputs=[selected_id, name, country, denom, desc],
            outputs=[save_btn, edit_btn, save_msg],
        )

        def navigate(delta):
            stamps = load_gallery("")
            ids = [row[0] for row in stamps]
            if selected_id.value in ids:
                idx = ids.index(selected_id.value) + delta
                idx = max(0, min(len(ids) - 1, idx))
            else:
                idx = 0
            return populate_stamp(ids[idx])

        nav_prev.click(lambda: navigate(-1), outputs=[selected_id, image, name, country, denom, desc])
        nav_next.click(lambda: navigate(1), outputs=[selected_id, image, name, country, denom, desc])

    with gr.Tab("Export"):
        export_csv_btn = gr.Button("Export CSV", visible=CONFIG["export_options"].get("csv", True))
        export_xlsx_btn = gr.Button("Export XLSX", visible=CONFIG["export_options"].get("xlsx", True))
        export_pdf_btn = gr.Button("Export PDF", visible=CONFIG["export_options"].get("pdf", True))
        export_status = gr.Textbox(label="Status")

        export_csv_btn.click(lambda: export_csv(), outputs=export_status)
        export_xlsx_btn.click(lambda: export_xlsx(), outputs=export_status)
        export_pdf_btn.click(lambda: export_pdf(), outputs=export_status)

    with gr.Tab("Settings"):
        cfg = load_config()
        ai_model = gr.Dropdown(["phi3", "custom", "manual"], value=cfg.get("ai_model", "phi3"), label="AI Model")
        with gr.Group():
            gr.Markdown("### Export options")
            csv = gr.Checkbox(value=cfg["export_options"].get("csv", True), label="CSV")
            xlsx = gr.Checkbox(value=cfg["export_options"].get("xlsx", True), label="XLSX")
            pdf = gr.Checkbox(value=cfg["export_options"].get("pdf", True), label="PDF")
            ebay = gr.Checkbox(value=cfg["export_options"].get("ebay", False), label="eBay")
            hipstamp = gr.Checkbox(value=cfg["export_options"].get("hipstamp", False), label="HipStamp")
            colnect = gr.Checkbox(value=cfg["export_options"].get("colnect", False), label="Colnect")
            stampworld = gr.Checkbox(value=cfg["export_options"].get("stampworld", False), label="StampWorld")
        save_settings_btn = gr.Button("Save Settings")
        settings_status = gr.Textbox(label="Status")
        save_settings_btn.click(
            save_settings,
            inputs=[ai_model, csv, xlsx, pdf, ebay, hipstamp, colnect, stampworld],
            outputs=settings_status,
        )

    with gr.Tab("Errors"):
        log_content = gr.Textbox(label="errors.log", lines=20)
        demo.load(read_errors, outputs=log_content)

# End of Blocks

def run():  # pragma: no cover - manual start helper
    demo.launch()


if __name__ == "__main__":  # pragma: no cover
    run()
