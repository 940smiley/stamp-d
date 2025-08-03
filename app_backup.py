from __future__ import annotations
import os
import requests
import base64
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from db import Session, Stamp
from image_utils import enhance_and_crop, is_duplicate, classify_image
from export_utils import export_csv
from ai_utils import generate_description
from parsing_utils import parse_title
# ...existing code...
def reverse_image_lookup(image_path):
    # Dummy implementation; replace with actual reverse search logic
    return f"Reverse search results for {os.path.basename(str(image_path))}" if image_path else "No image provided."
"""Main Gradio application for Stamp'd.

The UI exposes functionality for scanning stamps using a local Ollama
model, managing the gallery, exporting data and adjusting settings.  The
implementation focuses on being robust in a variety of environments – if
optional dependencies are missing the features gracefully degrade.
"""



# ---------------- Reverse Search ----------------
def search_relevant_sources(image_path):
    """Run refined searches for eBay sold items, Colnect, HipStamp."""
    if not image_path or not os.path.exists(image_path):
        return ("❌ Image not found.", "", "", "No match found", "")

    query = os.path.basename(image_path).replace("_", " ")
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={query}&LH_Sold=1"
    colnect_url = f"https://colnect.com/en/stamps/list/{query}"
    hipstamp_url = f"https://www.hipstamp.com/search?keywords={query}&show=store_items"

    # Try scrape top eBay match
    try:
        r = requests.get(ebay_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        item = soup.select_one(".s-item__title")
        top_title = item.text if item else "No match found"
    except requests.exceptions.RequestException:
        top_title = "No match found"

    return (
        f'<iframe src="{ebay_url}" width="100%" height="350"></iframe>',
        f'<iframe src="{colnect_url}" width="100%" height="350"></iframe>',
        f'<iframe src="{hipstamp_url}" width="100%" height="350"></iframe>',
        top_title,
        query
    )

# ---------------- Upload ----------------
def preview_upload(files):
    """Preview uploaded files with AI-generated metadata."""
    if not files:
        return []
    
    data = []
    for file in files:
        try:
            # Generate description using AI
            description = generate_description(file.name)
            
            # Parse the description to extract metadata
            country, denom, year = parse_title(description)
            
            data.append([file.name, country, denom, year, description])
        except Exception as e:
            data.append([file.name, "Unknown", "", "", f"Error: {str(e)}"])
    
    return data

def upload_reverse_search(idx, preview_data):
    """Reverse search for a specific uploaded image."""
    if not preview_data or idx >= len(preview_data):
        return ("❌ Invalid selection", "", "", "No match found")
    
    image_path = preview_data[idx][0]
    return search_relevant_sources(image_path)

def save_uploads(preview_data):
    """Save uploaded stamps to database."""
    if not preview_data:
        return "❌ No data to save"
    
    session = Session()
    saved_count = 0
    
    for row in preview_data:
        try:
            image_path, country, denom, year, notes = row
            
            # Check for duplicates
            if is_duplicate(image_path):
                continue
                
            # Create new stamp record
            stamp = Stamp(
                image_path=image_path,
                country=country,
                denomination=denom,
                year=year,
                notes=notes
            )
            session.add(stamp)
            saved_count += 1
            
        except Exception as e:
            continue
    
    session.commit()
    return f"✅ Saved {saved_count} stamps to database"

# ---------------- Gallery ----------------
def load_gallery_table():
    session = Session()
    stamps = session.query(Stamp).all()
    data = []
    for s in stamps:
        # Create thumbnail markdown
        if s.image_path and os.path.exists(s.image_path):
            thumb = f"![thumb]({s.image_path})"
        else:
            thumb = ""
                thumb = ""
        else:
            thumb = ""
        data.append([thumb, s.id, s.country, s.denomination, s.year, s.notes])
    return data

def load_gallery_images():
    session = Session()
    stamps = session.query(Stamp).all()
    return [(s.image_path, f"ID {s.id}: {s.country}") for s in stamps]

def load_stamp_details(stamp_id):
    session = Session()
    s = session.query(Stamp).get(int(stamp_id))
    if s:
        return s.id, s.image_path, s.country, s.denomination, s.year, s.notes
    return "", "", "", "", "", ""

def update_stamp_details(stamp_id, country, denomination, year, notes):
    session = Session()
    s = session.query(Stamp).get(int(stamp_id))
    if s:
        s.country = country
        s.denomination = denomination
        s.year = year
        s.notes = notes
        session.commit()
        return f"✅ Updated Stamp ID {stamp_id}"
    return "❌ Stamp not found."

# ---------------- Export ----------------
def export_data():
    return f"📁 Exported to {export_csv()}"

# ---------------- UI ----------------
with gr.Blocks(elem_id="app-container") as demo:
    gr.Markdown("# 📬 Stamp'd 9.1 - Clean Merge")
    gr.HTML("""
    <link rel='stylesheet' href='layout.css'>
    <script src='sortable.min.js'></script>
    <script src='layout.js'></script>
    """)

    # Upload Tab
    with gr.Tab("➕ Upload Stamps"):
        images = gr.File(file_types=["image"], file_count="multiple", label="Upload Stamp Images")
        preview_table = gr.Dataframe(
            headers=["Image Path", "Country", "Denomination", "Year", "Notes"],
            datatype=["str", "str", "str", "str", "str"],
            row_count="dynamic"
        )
        images.upload(preview_upload, images, preview_table)

        idx_input = gr.Number(label="Row Index (0-based)", precision=0)
        reverse_btn_upload = gr.Button("🔎 Reverse Image Search (Selected)")

        ebay_frame = gr.HTML(visible=False)
        colnect_frame = gr.HTML(visible=False)
        hipstamp_frame = gr.HTML(visible=False)
        suggested_title = gr.Textbox(label="Top eBay Match Title", visible=False)

        reverse_btn_upload.click(
            upload_reverse_search,
            inputs=[idx_input, preview_table],
            outputs=[ebay_frame, colnect_frame, hipstamp_frame, suggested_title]
        )

        save_btn = gr.Button("💾 Save to Database")
        save_status = gr.Textbox(label="Save Status")
        save_btn.click(save_uploads, preview_table, save_status)

    # Scan Tab
    with gr.Tab("🔍 Scan"):
        scan_input = gr.File(file_types=["image"], file_count="multiple", label="Select Images to Scan")
        scan_btn = gr.Button("🚀 Start Scan")
        scan_progress = gr.Textbox(label="Scan Progress")
        scan_results = gr.Dataframe(
            headers=["Image", "Country", "Denomination", "Year", "Notes"],
            datatype=["str", "str", "str", "str", "str"]
        )

        def scan_images(files):
            if not files:
                return "❌ No files selected", []
            
            results = []
            for i, file in enumerate(files):
                try:
                    # Update progress
                    progress = f"Processing {i+1}/{len(files)}: {file.name}"
                    yield progress, results
                    
                    # Generate description
                    description = generate_description(file.name)
                    country, denom, year = parse_title(description)
                    
                    results.append([file.name, country, denom, year, description])
                    
                except Exception as e:
                    results.append([file.name, "Error", "", "", str(e)])
            
            yield f"✅ Completed scanning {len(files)} images", results

        scan_btn.click(scan_images, scan_input, [scan_progress, scan_results])

    # Gallery Tab
    with gr.Tab("📋 Gallery"):
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh")
            view_switch = gr.Radio(["Table View", "Images Only"], value="Table View", label="View Mode")

        gallery_table = gr.Dataframe(
            headers=["Image", "ID", "Country", "Denomination", "Year", "Notes"],
            datatype=["markdown", "number", "str", "str", "str", "str"],
            row_count="dynamic"
        )

        stamp_id = gr.Textbox(label="Stamp ID", interactive=False)
        image_display = gr.Image(label="Stamp Image")
        country_edit = gr.Textbox(label="Country")
        denom_edit = gr.Textbox(label="Denomination")
        year_edit = gr.Textbox(label="Year")
        notes_edit = gr.Textbox(label="Notes", lines=3)
        update_status = gr.Textbox(label="Update Status")

        reverse_btn_gallery = gr.Button("🔎 Reverse Image Search (Inline)")
        ebay_frame_g = gr.HTML(visible=False)
        colnect_frame_g = gr.HTML(visible=False)
        hipstamp_frame_g = gr.HTML(visible=False)
        suggested_title_g = gr.Textbox(label="Top eBay Match Title", visible=False)

        def gallery_reverse_search(sid):
            if sid:
                stamp = Session().query(Stamp).get(int(sid))
                if stamp:
                    ebay, colnect, hip, title, query = search_relevant_sources(stamp.image_path)
                    year, country, denom = parse_title(title)
def gallery_reverse_search(sid):
            if sid:
                try:
                    stamp = Session().query(Stamp).get(int(sid))
                    if stamp:
                        ebay, colnect, hip, title, query = search_relevant_sources(stamp.image_path)
                        year, country, denom = parse_title(title)
                        return (ebay, colnect, hip, title, country, denom, year)
                except Exception as e:
                    return (f"❌ Error: {str(e)}", "", "", "", "", "", "")
            return ("❌ No stamp selected", "", "", "", "", "", "")

        reverse_btn_gallery.click(
suggested_title_g = gr.Textbox(label="Top eBay Match Title", visible=False)

        def gallery_reverse_search(sid):
            # import logging
            logging.info(f"Entering gallery_reverse_search with sid: {sid}")
            if sid:
                stamp = Session().query(Stamp).get(int(sid))
                if stamp:
                    logging.info(f"Found stamp with id: {sid}")
                    ebay, colnect, hip, title, query = search_relevant_sources(stamp.image_path)
                    year, country, denom = parse_title(title)
                    logging.info(f"Reverse search completed for stamp id: {sid}")
                    return (ebay, colnect, hip, title, country, denom, year)
            logging.warning("No stamp selected or stamp not found")
            return ("❌ No stamp selected", "", "", "", "", "", "")

        reverse_btn_gallery.click(

        reverse_btn_gallery.click(
            gallery_reverse_search,
            inputs=stamp_id,
            outputs=[ebay_frame_g, colnect_frame_g, hipstamp_frame_g, suggested_title_g,
                     country_edit, denom_edit, year_edit]
        )

        update_btn = gr.Button("💾 Update Stamp")
        update_btn.click(update_stamp_details,
                         [stamp_id, country_edit, denom_edit, year_edit, notes_edit],
                         update_status)


def populate_details(stamp_id):
    return get_stamp_by_id(stamp_id)

        def toggle_views(view_mode):
            return (gr.update(visible=(view_mode == "Table View")),
                    gr.update(visible=(view_mode == "Images Only")))

# === UI ===
with gr.Blocks(title="Stamp'd") as demo:
    gr.Markdown("# 📬 Stamp'd — Smart Stamp Cataloging")

        gallery_table.select(
            lambda evt: load_stamp_details(evt.value[1]),
            None,
            [stamp_id, image_display, country_edit, denom_edit, year_edit, notes_edit]
        )
        gallery_images.select(
            lambda label: load_stamp_details(label.split(":")[0].replace("ID ", "")),
            None,
            [stamp_id, image_display, country_edit, denom_edit, year_edit, notes_edit]
        )

    # Export Tab
    with gr.Tab("⬇️ Export"):
        export_btn = gr.Button("Export CSV")
        export_status = gr.Textbox(label="Export Status")
        export_btn.click(export_data, outputs=export_status)

demo.launch()

