import gradio as gr
import os, requests, base64
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from db import Session, Stamp
from image_utils import enhance_and_crop, is_duplicate, classify_image
from export_utils import export_csv
from ai_utils import generate_description
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------- Reverse Search ----------------
def search_sources(image_path):
    """Generate marketplace URLs based on an image file path."""
# import re  # Used for sanitizing input to prevent log injection

def search_sources(image_path):
    """Generate marketplace URLs based on an image file path."""
    sanitized_path = re.sub(r'[
\r]', '', str(image_path))  # Sanitize input
    logger.info(f"Attempting reverse search for image_path: {sanitized_path}")
    if not image_path or not os.path.exists(image_path):
        logger.error(f"Invalid image path for search: {sanitized_path}")
        return "❌ No image", "❌ No image", "❌ No image"

    filename_without_ext = os.path.splitext(os.path.basename(image_path))[0]
    if not image_path or not os.path.exists(image_path):
# import html  # Used to escape special characters in user input to prevent log injection
def search_sources(image_path):
    """Generate marketplace URLs based on an image file path."""
    logger.info(f"Attempting reverse search for image_path: {html.escape(image_path)}")
    if not image_path or not os.path.exists(image_path):
        logger.error(f"Invalid image path for search: {html.escape(image_path)}")
        return "❌ No image", "❌ No image", "❌ No image"

    filename_without_ext = os.path.splitext(os.path.basename(image_path))[0]
    query = filename_without_ext.replace("_", " ")

    ebay = f"https://www.ebay.com/sch/i.html?_nkw={html.escape(query)}&LH_Sold=1"
    colnect = f"https://colnect.com/en/stamps/list/{html.escape(query)}"
    hip = f"https://www.hipstamp.com/search?keywords={html.escape(query)}&show=store_items"

    logger.info(f"Generated eBay URL: {html.escape(ebay)}")
    logger.info(f"Generated Colnect URL: {html.escape(colnect)}")
    logger.info(f"Generated HipStamp URL: {html.escape(hip)}")

    return (
        f"<a href='{html.escape(ebay)}' target='_blank'>eBay Results</a>",
        f"<a href='{html.escape(colnect)}' target='_blank'>Colnect Results</a>",
        f"<a href='{html.escape(hip)}' target='_blank'>HipStamp Results</a>"
    )
        return "❌ No image", "❌ No image", "❌ No image"

    filename_without_ext = os.path.splitext(os.path.basename(image_path))[0]
    query = filename_without_ext.replace("_", " ")

    ebay = f"https://www.ebay.com/sch/i.html?_nkw={query}&LH_Sold=1"
    colnect = f"https://colnect.com/en/stamps/list/{query}"
    hip = f"https://www.hipstamp.com/search?keywords={query}&show=store_items"

    logger.info(f"Generated eBay URL: {ebay}")
    logger.info(f"Generated Colnect URL: {colnect}")
    logger.info(f"Generated HipStamp URL: {hip}")

    return (
        f"<a href='{ebay}' target='_blank'>eBay Results</a>",
        f"<a href='{colnect}' target='_blank'>Colnect Results</a>",
        f"<a href='{hip}' target='_blank'>HipStamp Results</a>"
    )

# ---------------- Upload ----------------
def preview_upload(images):
    rows = []
    if not images:
        return rows
    for path in images:
        thumb_html = path
        if os.path.exists(path):
            with Image.open(path) as img:
                img.thumbnail((64, 64))
                buf = BytesIO()
                img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            thumb_html = f"<img src='data:image/png;base64,{b64}' width='50'/>"
        else:
            logger.warning(f"File not found during preview: {path}")
            thumb_html = "File not found"

        country = classify_image(path) if os.path.exists(path) else "Unknown"
        from types import SimpleNamespace
        desc_obj = SimpleNamespace(country=country, year="Unknown")
        desc = generate_description(desc_obj)
        rows.append([thumb_html, path, country, "", "", desc])
    return rows

def save_upload(preview_rows):
    if not preview_rows:
        return "❌ No rows to save"
    session = Session()
    try:
        saved_count = 0
        for row in preview_rows:
            if len(row) < 6:
saved_count = 0
        for row in preview_rows:
            if len(row) < 6:
                # Use repr() to safely represent the row content in the log
                logger.warning(f"Skipping malformed row during save_upload: {repr(row)}")
                continue
            _, path, country, denom, year, notes = row
            if not os.path.exists(path):
                continue
            _, path, country, denom, year, notes = row
            if not os.path.exists(path):
# Import re for regular expression operations
# Used to sanitize log input by removing newline characters
import re

def save_upload(preview_rows):
    if not preview_rows:
        return "❌ No rows to save"
    session = Session()
    try:
        saved_count = 0
        for row in preview_rows:
            if len(row) < 6:
                logger.warning(f"Skipping malformed row during save_upload: {row}")
                continue
            _, path, country, denom, year, notes = row
            if not os.path.exists(path):
                sanitized_path = re.sub(r'[
\r]', '', path)  # Remove newline characters
                logger.warning(f"File not found during save: {sanitized_path}")
                continue
            if is_duplicate(path, session):
                logger.info(f"Skipping duplicate image: {path}")
                continue
            stamp = Stamp(
                image_path=path,
                country=country,
                continue
            if is_duplicate(path, session):
# Import logging module for safe logging practices
import logging

def save_upload(preview_rows):
    if not preview_rows:
        return "❌ No rows to save"
    session = Session()
    try:
        saved_count = 0
        for row in preview_rows:
            if len(row) < 6:
                logger.warning("Skipping malformed row during save_upload: %s", row)
                continue
            _, path, country, denom, year, notes = row
            if not os.path.exists(path):
                logger.warning("File not found during save: %s", path)
                continue
            if is_duplicate(path, session):
                logging.info("Skipping duplicate image: %s", path)
                continue
            stamp = Stamp(
                image_path=path,
                country=country,
                denomination=denom,
                continue
            stamp = Stamp(
                image_path=path,
                country=country,
                denomination=denom,
                year=year,
                notes=notes,
                description=notes
            )
            session.add(stamp)
            saved_count += 1
        session.commit()
        return f"✅ Saved {saved_count} stamps to database!"
    except Exception as e:
        logger.exception("Error saving uploads")
        session.rollback()
        return "❌ Error saving to database"

def save_upload_and_refresh(preview_rows):
    status = save_upload(preview_rows)
    return status, load_gallery_data()

# ---------------- Gallery ----------------
def load_gallery_data():
    session = Session()
    data = []
    for s in session.query(Stamp).all():
        thumb_html = s.image_path
        if os.path.exists(s.image_path):
            with Image.open(s.image_path) as img:
                img.thumbnail((64, 64))
                buf = BytesIO()
                img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            thumb_html = f"<img src='data:image/png;base64,{b64}' width='50'/>"
        data.append([thumb_html, s.id, s.country, s.denomination, s.year, s.notes])
    return data

def update_gallery_table(new_table):
    """Update database with inline edits."""
    session = Session()
    try:
        for row in new_table:
            if len(row) < 6:
try:
        for row in new_table:
            if len(row) < 6:
                # Use string formatting to sanitize input
                logger.warning("Skipping malformed row during update_gallery_table: %s", str(row))
                continue
            thumb, stamp_id, country, denom, year, notes = row
            try:
                stamp_id = int(stamp_id)
            except (ValueError, TypeError):
                logger.error("Invalid stamp_id encountered during update: %s", str(stamp_id))
                continue

            s = session.query(Stamp).get(stamp_id)
            if s:
                s.country, s.denomination, s.year, s.notes = country, denom, year, notes
            else:
                logger.warning("Stamp with ID %s not found for update.", str(stamp_id))
        session.commit()
        return "✅ Changes saved inline!"
    except Exception:
                continue
            thumb, stamp_id, country, denom, year, notes = row
            try:
                stamp_id = int(stamp_id)
            except (ValueError, TypeError):
# Import logging and html modules
import logging
import html

def update_gallery_table(new_table):
    """Update database with inline edits."""
    session = Session()
    try:
        for row in new_table:
            if len(row) < 6:
                logger.warning(f"Skipping malformed row during update_gallery_table: {row}")
                continue
            thumb, stamp_id, country, denom, year, notes = row
            try:
                stamp_id = int(stamp_id)
            except (ValueError, TypeError):
                # Sanitize user input before logging
                safe_stamp_id = html.escape(str(stamp_id))
                logger.error(f"Invalid stamp_id encountered during update: {safe_stamp_id}")
                continue

            s = session.query(Stamp).get(stamp_id)
            if s:
                s.country, s.denomination, s.year, s.notes = country, denom, year, notes
            else:
                logger.warning(f"Stamp with ID {stamp_id} not found for update.")
                continue

            s = session.query(Stamp).get(stamp_id)
            if s:
                s.country, s.denomination, s.year, s.notes = country, denom, year, notes
            else:
try:
        for row in new_table:
            if len(row) < 6:
                logger.warning("Skipping malformed row during update_gallery_table: %s", row)
                continue
            thumb, stamp_id, country, denom, year, notes = row
            try:
                stamp_id = int(stamp_id)
            except (ValueError, TypeError):
                logger.error("Invalid stamp_id encountered during update: %s", stamp_id)
                continue

            s = session.query(Stamp).get(stamp_id)
            if s:
                s.country, s.denomination, s.year, s.notes = country, denom, year, notes
            else:
                logger.warning("Stamp with ID %s not found for update.", stamp_id)
        session.commit()
        return "✅ Changes saved inline!"
    except Exception:
        session.commit()
        return "✅ Changes saved inline!"
    except Exception:
        logger.exception("Error updating gallery table")
        session.rollback()
        return "❌ Error saving changes"

def load_details(selected_row_data):
    """Return stamp details for a row selected in the gallery."""
    if not selected_row_data or len(selected_row_data) < 2:
        logger.warning("No row data or insufficient row data for load_details.")
        return "", None, "", "", "", ""

    stamp_id_str = selected_row_data[1]
    try:
        stamp_id = int(stamp_id_str)
    except (ValueError, TypeError):
        logger.error(f"Invalid stamp ID from selected row: {stamp_id_str}")
        return "", None, "", "", "", ""

    session = Session()
logger.error(f"Invalid stamp ID from selected row: {stamp_id_str}")
        return "", None, "", "", "", ""

    session = Session()
    try:
        s = session.query(Stamp).get(stamp_id)
        if not s:
            logger.warning(f"Stamp with ID {stamp_id} not found in database.")
            return "", None, "", "", "", ""
        return s.id, s.image_path, s.country, s.denomination, s.year, s.notes
    except Exception as e:
        logger.exception(f"Error querying database for stamp ID {stamp_id}")
        return "", None, "", "", "", ""
    finally:
        session.close()

# ---------------- Export ----------------
def export_data():
    return f"📁 Exported to {export_csv()}"

# ---------------- UI ----------------
with gr.Blocks(css="#app-container{padding:10px;}") as demo:
    gr.Markdown("# 📬 Stamp'd – Inline Editing Version")

    # --- Upload Tab ---
    with gr.Tab("➕ Upload"):
        upload_files = gr.File(file_types=["image"], file_count="multiple", label="Upload Stamp Images")
    if not s:
        logger.warning(f"Stamp with ID {stamp_id} not found in database.")
        return "", None, "", "", "", ""

    return s.id, s.image_path, s.country, s.denomination, s.year, s.notes

# ---------------- Export ----------------
def export_data():
    return f"📁 Exported to {export_csv()}"

# ---------------- UI ----------------
with gr.Blocks(css="#app-container{padding:10px;}") as demo:
    gr.Markdown("# 📬 Stamp’d – Inline Editing Version")

    # --- Upload Tab ---
    with gr.Tab("➕ Upload"):
        upload_files = gr.File(file_types=["image"], file_count="multiple", label="Upload Stamp Images")
        preview_table = gr.Dataframe(
            headers=["Thumb", "Path", "Country", "Denom", "Year", "Notes"],
            datatype=["markdown", "str", "str", "str", "str", "str"],
            row_count="dynamic"
        )
        upload_files.upload(preview_upload, upload_files, preview_table)

        idx = gr.Number(label="Row Index", precision=0)
        btn_rev_upload = gr.Button("🔎 Reverse Search Selected")
        ebay_iframe_u = gr.HTML()
        colnect_iframe_u = gr.HTML()
        hip_iframe_u = gr.HTML()
        btn_rev_upload.click(
            lambda i, table: search_sources(table[int(i)][1]) if 0 <= int(i) < len(table) else ("❌", "❌", "❌"),
            [idx, preview_table], [ebay_iframe_u, colnect_iframe_u, hip_iframe_u]
        )

        save_status = gr.Textbox(label="Save Status")
        btn_save = gr.Button("💾 Save All")

    # --- Gallery Tab ---
    with gr.Tab("📋 Gallery"):
        btn_refresh = gr.Button("🔄 Refresh")
        gallery_table = gr.Dataframe(
            headers=["Thumb", "ID", "Country", "Denom", "Year", "Notes"],
            datatype=["markdown", "number", "str", "str", "str", "str"],
            row_count="dynamic",
            interactive=True   # Enable inline editing
        )
        gallery_table.change(update_gallery_table, gallery_table, None)  # Auto-save on change
        btn_refresh.click(load_gallery_data, outputs=gallery_table)

        stamp_id_display = gr.Textbox(label="Selected Stamp ID", interactive=False)
        image_display = gr.Image(label="Selected Stamp Image", type="filepath")
        btn_rev_gallery = gr.Button("🔎 Reverse Search Selected")
        ebay_iframe_g = gr.HTML()
        colnect_iframe_g = gr.HTML()
        hip_iframe_g = gr.HTML()

        def _on_gallery_select(evt: gr.SelectData, table):
            if not evt or table is None:
                return "", None, "", "", "", ""
            idx = evt.index if isinstance(evt.index, int) else evt.index[0]
            if idx is None or idx >= len(table):
                return "", None, "", "", "", ""
            return load_details(table[idx])

        gallery_table.select(
            _on_gallery_select,
            [gallery_table],
            [stamp_id_display, image_display, gr.Textbox(visible=False), gr.Textbox(visible=False), gr.Textbox(visible=False), gr.Textbox(visible=False)]
        )

        btn_rev_gallery.click(
            lambda img_path: search_sources(img_path) if img_path else ("❌", "❌", "❌"),
            inputs=image_display,
            outputs=[ebay_iframe_g, colnect_iframe_g, hip_iframe_g]
        )

    # --- Export Tab ---
    with gr.Tab("⬇️ Export"):
        btn_export = gr.Button("Export CSV")
        export_status = gr.Textbox()
        btn_export.click(export_data, outputs=export_status)

demo.load(load_gallery_data, None, gallery_table)
btn_save.click(save_upload_and_refresh, preview_table, [save_status, gallery_table])

demo.launch()
