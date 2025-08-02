# app.py — Main application for Stamp'd

import os
import gradio as gr
import logging
from db_utils import init_db, get_all_stamps, insert_stamp, update_stamp, get_stamp_by_id
from ai_utils import generate_description, classify_image
from export_utils import export_csv
from reverse_search import search_sources
from config import *

# Ensure folders exist
for dir_path in [IMAGES_DIR, THUMBNAILS_DIR, LOGS_DIR, BACKUP_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Logging
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "errors.log"),
    level=logging.ERROR,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

# Initialize DB
init_db()

def sync_and_autofill():
    previews = []
    for fname in os.listdir(IMAGES_DIR):
        if fname.lower().endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(IMAGES_DIR, fname)
            stamp_data = {
                "image_path": img_path,
                "country": "",
                "denomination": "",
                "year": "",
                "notes": "",
                "catalog_number": "",
                "mint_used": "",
                "description": generate_description(img_path),
                "ai_classification": classify_image(img_path)
            }
            previews.append(stamp_data)
    return previews

def save_previews(preview_list):
    for entry in preview_list:
        insert_stamp(entry)
    return "✅ Saved new stamps!"

def reverse_image_lookup(image_path):
    try:
        results = search_sources(image_path)
        # Format results as HTML list
        html = "<ul>"
        for r in results:
            html += f"<li>{r}</li>"
        html += "</ul>"
        return html
    except Exception as e:
        logging.error(f"Reverse search error: {str(e)}")
        return "<ul><li>❌ Error during reverse search</li></ul>"

def refresh_gallery():
    return get_all_stamps()

def populate_details(stamp_id):
    return get_stamp_by_id(stamp_id)

def update_stamp_details(stamp_id, country, denomination, year, notes, catalog, mint_used):
    return update_stamp(stamp_id, country, denomination, year, notes, catalog, mint_used)

# === UI ===
with gr.Blocks(title="Stamp’d") as demo:
    gr.Markdown("# 📬 Stamp’d — Smart Stamp Cataloging")

    with gr.Tab("📂 Sync & Autofill"):
        sync_btn = gr.Button("🔁 Sync Folder and Autofill")
        preview_list = gr.Dataframe(headers=["image_path", "country", "denomination", "year", "notes", "catalog_number", "mint_used", "description", "ai_classification"])
        save_btn = gr.Button("💾 Save to DB")
        sync_status = gr.Textbox(label="Status")

        sync_btn.click(fn=sync_and_autofill, outputs=preview_list)
        save_btn.click(fn=save_previews, inputs=preview_list, outputs=sync_status)

    with gr.Tab("🖼️ Gallery"):
        gallery = gr.Dataframe(headers=["id", "thumb", "country", "denomination", "year", "catalog_number", "mint_used", "notes"])
        refresh_btn = gr.Button("🔄 Refresh Gallery")
        refresh_btn.click(fn=refresh_gallery, outputs=gallery)

        selected_id = gr.Number(label="Selected ID", precision=0)
        image = gr.Image()
        country = gr.Textbox(label="Country")
        denom = gr.Textbox(label="Denomination")
        year = gr.Textbox(label="Year")
        notes = gr.Textbox(label="Notes")
        catalog = gr.Textbox(label="Catalog Number")
        mint_used = gr.Textbox(label="Mint/Used")
        update_status = gr.Textbox(label="Update Result")

        gallery.select(fn=populate_details, inputs=[selected_id],
                       outputs=[selected_id, image, country, denom, year, notes, catalog, mint_used])

        update_btn = gr.Button("💾 Update Selected")
        update_btn.click(fn=update_stamp_details,
                         inputs=[selected_id, country, denom, year, notes, catalog, mint_used],
                         outputs=update_status)

        reverse_btn = gr.Button("🔍 Reverse Image Search")
        reverse_result = gr.HTML()

        # Use image path from selected_id (stamp details)
        reverse_btn.click(fn=reverse_image_lookup, inputs=[image], outputs=reverse_result)

    with gr.Tab("📤 Export & Logs"):
        export_btn = gr.Button("Export CSV")
        export_msg = gr.Textbox()
        export_btn.click(fn=export_csv, outputs=export_msg)

        log_viewer = gr.File(label="Error Log")
        log_viewer.value = os.path.join(LOGS_DIR, "errors.log")

demo.launch(share=True)
