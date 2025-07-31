import gradio as gr
import os, requests, base64
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from db import Session, Stamp # Assuming db.py and Stamp class are correctly defined
from image_utils import enhance_and_crop, is_duplicate, classify_image # Assuming these are defined
from export_utils import export_csv # Assuming this is defined
from ai_utils import generate_description # Assuming this is defined
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------- Reverse Search ----------------
def search_sources(image_path):
    logger.info(f"Attempting reverse search for image_path: {image_path}")
    if not image_path or not os.path.exists(image_path):
        logger.error(f"Invalid image path for search: {image_path}")
        return "❌ No image", "❌ No image", "❌ No image"
    
    # Extract filename without extension for the query
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
        return [] # Return empty list if no images
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
            thumb_html = "File not found" # Indicate missing file

        # Placeholder for classify_image and generate_description if they rely on actual content
        # For now, let's assume they work or add more robust error handling
        country = classify_image(path) if os.path.exists(path) else "Unknown"
        desc_obj = type("S", (), {"country": country, "year": "Unknown"}) # Mock object for generate_description
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
            # Check if row has enough elements before unpacking
            if len(row) < 6:
                logger.warning(f"Skipping malformed row during save_upload: {row}")
                continue

            _, path, country, denom, year, notes = row
            if not os.path.exists(path):
                logger.warning(f"File not found during save: {path}")
                continue
            if is_duplicate(path, session):
                logger.info(f"Skipping duplicate image: {path}")
                continue
            stamp = Stamp(
                image_path=path,
                country=country,
                denomination=denom,
                year=year,
                notes=notes,
                description=notes # Often description is just notes for simplicity
            )
            session.add(stamp)
            saved_count += 1
        session.commit()
        return f"✅ Saved {saved_count} stamps to database!"
    except Exception as e:
        logger.exception("Error saving uploads")
        session.rollback()
        return f"❌ Error saving to database: {e}"

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
        else:
            logger.warning(f"Image file not found for stamp ID {s.id}: {s.image_path}")
            thumb_html = "File not found" # Indicate missing file in gallery

        data.append([thumb_html, s.id, s.country, s.denomination, s.year, s.notes])
    return data

def update_gallery_table(new_table):
    """Update database with inline edits."""
    session = Session()
    try:
        for row in new_table:
            # Ensure row has enough elements
            if len(row) < 6:
                logger.warning(f"Skipping malformed row during update_gallery_table: {row}")
                continue

            thumb, stamp_id, country, denom, year, notes = row
            # Convert stamp_id to int securely
            try:
                stamp_id = int(stamp_id)
            except (ValueError, TypeError):
                logger.error(f"Invalid stamp_id encountered during update: {stamp_id}")
                continue # Skip this row if ID is invalid

            s = session.query(Stamp).get(stamp_id)
            if s:
                s.country, s.denomination, s.year, s.notes = country, denom, year, notes
            else:
                logger.warning(f"Stamp with ID {stamp_id} not found for update.")
        session.commit()
        return "✅ Changes saved inline!"
    except Exception as e:
        logger.exception("Error updating gallery table")
        session.rollback()
        return f"❌ Error saving changes: {e}"


def load_details(selected_row_data):
    """
    Loads details for the selected stamp from the gallery table.
    `selected_row_data` will be a list containing the values of the selected row.
    """
    if not selected_row_data or len(selected_row_data) < 2:
        logger.warning("No row data or insufficient row data for load_details.")
        return "", None, "", "", "", "" # Return empty values if no data

    stamp_id_str = selected_row_data[1] # The ID is the second element
    try:
        stamp_id = int(stamp_id_str)
    except (ValueError, TypeError):
        logger.error(f"Invalid stamp ID from selected row: {stamp_id_str}")
        return "", None, "", "", "", ""

    session = Session()
    s = session.query(Stamp).get(stamp_id)
    if not s:
        logger.warning(f"Stamp with ID {stamp_id} not found in database.")
        return "", None, "", "", "", ""
    
    # Return all details, including image_path for display
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

        idx = gr.Number(label="Row Index (for Reverse Search)", precision=0)
        btn_rev_upload = gr.Button("🔎 Reverse Search Selected (Upload Tab)")
        ebay_iframe_u = gr.HTML(label="eBay Results")
        colnect_iframe_u = gr.HTML(label="Colnect Results")
        hip_iframe_u = gr.HTML(label="HipStamp Results")
        btn_rev_upload.click(
            lambda i, table: search_sources(table[int(i)][1]) if 0 <= int(i) < len(table) else ("❌ Invalid Row Index", "❌ Invalid Row Index", "❌ Invalid Row Index"),
            [idx, preview_table], [ebay_iframe_u, colnect_iframe_u, hip_iframe_u]
        )

        save_status = gr.Textbox(label="Save Status")
        btn_save = gr.Button("💾 Save All Uploaded Stamps")

    # --- Gallery Tab ---
    with gr.Tab("📋 Gallery"):
        btn_refresh = gr.Button("🔄 Refresh Gallery Data")
        gallery_table = gr.Dataframe(
            headers=["Thumb", "ID", "Country", "Denom", "Year", "Notes"],
            datatype=["markdown", "number", "str", "str", "str", "str"],
            row_count="dynamic",
            interactive=True   # Enable inline editing
        )
        gallery_table.change(update_gallery_table, gallery_table, None)  # Auto-save on change
        btn_refresh.click(load_gallery_data, outputs=gallery_table)

        with gr.Column(): # Group details and search buttons
            stamp_id_display = gr.Textbox(label="Selected Stamp ID", interactive=False)
            image_display = gr.Image(label="Selected Stamp Image", type="filepath") # Use filepath to directly display
            
            # Hidden textboxes to capture other details from load_details if needed elsewhere
            _country_hidden = gr.Textbox(visible=False)
            _denomination_hidden = gr.Textbox(visible=False)
            _year_hidden = gr.Textbox(visible=False)
            _notes_hidden = gr.Textbox(visible=False)

            btn_rev_gallery = gr.Button("🔎 Reverse Search Selected (Gallery Tab)")
            ebay_iframe_g = gr.HTML(label="eBay Results")
            colnect_iframe_g = gr.HTML(label="Colnect Results")
            hip_iframe_g = gr.HTML(label="HipStamp Results")

        # When a row is selected in the gallery, load its details
        gallery_table.select(
            lambda evt, table: (
                load_details(table[idx])
                if evt
                and table
                and 0 <= (idx := (evt.index if isinstance(evt.index, int) else evt.index[0])) < len(table)
                else ("", None, "", "", "", "")
            ),
            inputs=gallery_table,
            outputs=[
                stamp_id_display,
                image_display,
                _country_hidden,
                _denomination_hidden,
                _year_hidden,
                _notes_hidden,
            ],
        )

        # When the reverse search button is clicked, use the displayed image path
        btn_rev_gallery.click(
            lambda img_path: search_sources(img_path) if img_path else ("❌ No Image Selected", "❌ No Image Selected", "❌ No Image Selected"),
            inputs=image_display, # Now image_display correctly holds the path
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
