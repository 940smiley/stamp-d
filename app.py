import gradio as gr
import os, requests
import gradio as gr
import os, requests
from bs4 import BeautifulSoup
from db import Session, Stamp
from image_utils import enhance_and_crop, is_duplicate, classify_image
from export_utils import export_csv
from ai_utils import generate_description

# from shutil import specific_function  # Import specific function if needed
# from uuid import uuid4  # Import UUID generation function

# ---------------- Refined Reverse Search ----------------
def search_relevant_sources(image_path):
from bs4 import BeautifulSoup
from db import Session, Stamp
from image_utils import enhance_and_crop, is_duplicate, classify_image
from export_utils import export_csv
from ai_utils import generate_description

# ---------------- Refined Reverse Search ----------------
def search_relevant_sources(image_path):
    """Run refined searches for marketplaces and catalog sites."""
    results = {"ebay": "", "colnect": "", "hipstamp": ""}

    if not image_path or not os.path.exists(image_path):
        return "❌ Image not found.", "", "", "", ""

    # eBay sold listings
    query = os.path.basename(image_path).replace("_", " ")
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={query}&LH_Sold=1"
    colnect_url = f"https://colnect.com/en/stamps/list/{query}"
    hipstamp_url = f"https://www.hipstamp.com/search?keywords={query}&show=store_items"

    results["ebay"] = f'<a href="{ebay_url}" target="_blank">eBay Sold Items for "{query}"</a>'
    results["colnect"] = f'<a href="{colnect_url}" target="_blank">Colnect Matches for "{query}"</a>'
    results["hipstamp"] = f'<a href="{hipstamp_url}" target="_blank">HipStamp Items for "{query}"</a>'

    # Optionally scrape eBay sold items for top match title
    try:
        r = requests.get(ebay_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        item = soup.select_one(".s-item__title")
        top_title = item.text if item else ""
    except:
        top_title = ""

    return (
        f'<iframe src="{ebay_url}" width="100%" height="350"></iframe>',
        f'<iframe src="{colnect_url}" width="100%" height="350"></iframe>',
        f'<iframe src="{hipstamp_url}" width="100%" height="350"></iframe>',
        top_title
    )

# ---------------- Upload + Process ----------------
def preview_upload(images):
    preview_data = []
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    for img in images:
        # gr.File may pass either a path string or an object with a `.name` attribute
        img_path = img if isinstance(img, str) else getattr(img, "name", "")
        ext = os.path.splitext(img_path)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
img_path = img if isinstance(img, str) else getattr(img, "name", "")
        ext = os.path.splitext(img_path)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        # Use os.path.normpath and os.path.abspath to sanitize the path
        dest_path = os.path.abspath(os.path.normpath(os.path.join(upload_dir, unique_name)))
        if not dest_path.startswith(os.path.abspath(upload_dir)):
            raise ValueError("Invalid file path")
        shutil.copy(img_path, dest_path)
        enhance_and_crop(dest_path)
        country = classify_image(dest_path)
        shutil.copy(img_path, dest_path)
        enhance_and_crop(dest_path)
        country = classify_image(dest_path)
upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    for img in images:
        try:
            # gr.File may pass either a path string or an object with a `.name` attribute
            img_path = img if isinstance(img, str) else getattr(img, "name", "")
            ext = os.path.splitext(img_path)[1]
            unique_name = f"{uuid.uuid4()}{ext}"
            dest_path = os.path.join(upload_dir, unique_name)
            shutil.copy(img_path, dest_path)
            enhance_and_crop(dest_path)
            country = classify_image(dest_path)
            desc = generate_description(type("StampObj", (), {"country": country, "year": "Unknown"}))
            preview_data.append([dest_path, country, "", "", desc])
        except Exception as e:
            print(f"Error processing image {img_path}: {str(e)}")
    return preview_data

def save_upload(preview_table):
# ---------------- Upload + Process ----------------
def preview_upload(images):
    preview_data = []
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Import multiprocessing and functools
    import multiprocessing
    from functools import partial
    
    # Define a worker function to process each image
    def process_image(img, upload_dir):
        img_path = img if isinstance(img, str) else getattr(img, "name", "")
        ext = os.path.splitext(img_path)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        dest_path = os.path.join(upload_dir, unique_name)
        shutil.copy(img_path, dest_path)
        enhance_and_crop(dest_path)
        country = classify_image(dest_path)
        desc = generate_description(type("StampObj", (), {"country": country, "year": "Unknown"}))
        return [dest_path, country, "", "", desc]
    
    # Use multiprocessing to process images concurrently
    with multiprocessing.Pool() as pool:
        preview_data = pool.map(partial(process_image, upload_dir=upload_dir), images)
    
    return preview_data

def save_upload(preview_table):
    session = Session()
    for row in preview_table:
    return preview_data

def save_upload(preview_table):
    session = Session()
    for row in preview_table:
        image_path, country, denomination, year, notes = row
        if is_duplicate(image_path, session):
            continue
        stamp = Stamp(
            country=country,
            denomination=denomination,
            year=year,
            notes=notes,
            image_path=image_path,
            description=notes
        )
        session.add(stamp)
    session.commit()
    return "✅ Stamps saved successfully!"

# ---------------- Gallery ----------------
def load_gallery_data():
    session = Session()
    stamps = session.query(Stamp).all()
    data = []
    for s in stamps:
        thumb = s.image_path if os.path.exists(s.image_path) else ""
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
with gr.Blocks() as demo:
    gr.Markdown("# 📬 Stamp’d 7.0 - Inline Reverse Search & Copy")

    # Upload Tab
    with gr.Tab("➕ Upload Stamps"):
        images = gr.File(file_types=["image"], file_count="multiple", label="Upload Stamp Images")
        preview_table = gr.Dataframe(
            headers=["Image Path", "Country", "Denomination", "Year", "Notes"],
            datatype=["str", "str", "str", "str", "str"],
            row_count=3
        )
        images.upload(preview_upload, images, preview_table)

        with gr.Row():
            idx_input = gr.Number(label="Row Index (0-based)", precision=0)
            reverse_btn_upload = gr.Button("🔎 Reverse Image Search (Selected)")
        
        ebay_frame = gr.HTML()
        colnect_frame = gr.HTML()
        hipstamp_frame = gr.HTML()
        suggested_title = gr.Textbox(label="Top Match Title from eBay")
        
        reverse_btn_upload.click(
            lambda idx, table: search_relevant_sources(table[int(idx)][0]) if 0 <= int(idx) < len(table) else ("❌ Invalid index","","","",""),
            inputs=[idx_input, preview_table],
            outputs=[ebay_frame, colnect_frame, hipstamp_frame, suggested_title]
        )

        # Copy buttons
        with gr.Row():
            country = gr.Textbox(label="Country (Copy)")
            denom = gr.Textbox(label="Denomination (Copy)")
            year = gr.Textbox(label="Year (Copy)")
            notes = gr.Textbox(label="Notes (Copy)")
        
        save_status = gr.Textbox(label="Save Status")
        save_btn = gr.Button("💾 Save All")
        save_btn.click(save_upload, preview_table, save_status)

    # Gallery Tab
    with gr.Tab("📋 Gallery"):
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh")
            view_switch = gr.Radio(["Table View", "Images Only"], value="Table View", label="View Mode")
        
        gallery_table = gr.Dataframe(
            headers=["Image", "ID", "Country", "Denomination", "Year", "Notes"],
            datatype=["str", "number", "str", "str", "str", "str"],
            row_count=5
        )

        stamp_id = gr.Textbox(label="Stamp ID", interactive=False)
        image_display = gr.Image(label="Stamp Image")
        country_edit = gr.Textbox(label="Country")
        denom_edit = gr.Textbox(label="Denomination")
        year_edit = gr.Textbox(label="Year")
        notes_edit = gr.Textbox(label="Notes", lines=3)
        update_status = gr.Textbox(label="Update Status")

        reverse_btn_gallery = gr.Button("🔎 Reverse Image Search (Inline)")
        ebay_frame_g = gr.HTML()
        colnect_frame_g = gr.HTML()
        hipstamp_frame_g = gr.HTML()
        suggested_title_g = gr.Textbox(label="Top eBay Match Title")

        reverse_btn_gallery.click(
            lambda stamp_id: search_relevant_sources(Session().query(Stamp).get(int(stamp_id)).image_path) if stamp_id else ("❌ No stamp selected","","","",""),
            inputs=stamp_id,
            outputs=[ebay_frame_g, colnect_frame_g, hipstamp_frame_g, suggested_title_g]
        )

        update_btn = gr.Button("💾 Update Stamp")
        update_btn.click(
            update_stamp_details,
            [stamp_id, country_edit, denom_edit, year_edit, notes_edit],
            update_status
        )

        gallery_images = gr.Gallery(show_label=False, columns=5, elem_id="gallery_images")

        def toggle_views(view_mode):
            return (gr.update(visible=(view_mode=="Table View")),
                    gr.update(visible=(view_mode=="Images Only")))

        view_switch.change(toggle_views, view_switch, [gallery_table, gallery_images])
        refresh_btn.click(load_gallery_data, outputs=gallery_table)
        refresh_btn.click(load_gallery_images, outputs=gallery_images)

        gallery_table.select(
            lambda evt: load_stamp_details(evt.value[1]),
            None,
            [stamp_id, image_display, country_edit, denom_edit, year_edit, notes_edit]
        )

        gallery_images.select(
            lambda label: load_stamp_details(label.split(":")[0].replace("ID ","")),
            None,
            [stamp_id, image_display, country_edit, denom_edit, year_edit, notes_edit]
        )

    # Export Tab
    with gr.Tab("⬇️ Export"):
        export_btn = gr.Button("Export CSV")
        export_status = gr.Textbox(label="Export Status")
        export_btn.click(export_data, outputs=export_status)

demo.launch()
