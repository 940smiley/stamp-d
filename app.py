import gradio as gr
import os
import requests
import base64
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from db import Session, Stamp
from image_utils import is_duplicate
from export_utils import export_csv
from ai_utils import generate_metadata
from config import IMAGES_DIR


def classify_image(path: str) -> str:
    """Predict stamp country for the given image path."""
    return generate_metadata(path).get("country", "Unknown")


def generate_description(path: str) -> str:
    """Generate a text description for the given image."""
    return generate_metadata(path).get("description", "")


# ---------------- Reverse Search ----------------


def search_sources(image_path):
    if not image_path or not os.path.exists(image_path):
        return "❌ No image", "❌ No image", "❌ No image"
    query = os.path.basename(image_path).replace("_", " ")
    ebay = f"https://www.ebay.com/sch/i.html?_nkw={query}&LH_Sold=1"
    colnect = f"https://colnect.com/en/stamps/list/{query}"
    hip = f"https://www.hipstamp.com/search?keywords={query}&show=store_items"
    return (
        f"<iframe src='{ebay}' width='100%' height='300'></iframe>",
        f"<iframe src='{colnect}' width='100%' height='300'></iframe>",
        f"<iframe src='{hip}' width='100%' height='300'></iframe>"
    )

# ---------------- Upload ----------------


def preview_upload(images):
    rows = []
    for path in images:
        thumb_html = path
        if os.path.exists(path):
            with Image.open(path) as img:
                img.thumbnail((64, 64))
                buf = BytesIO()
# Import statements for the fix
import os
from pathlib import Path  # Used for secure path handling

def preview_upload(images):
    rows = []
    for path in images:
        thumb_html = path
        safe_path = Path(path).resolve()
        if safe_path.is_file() and safe_path.parent == Path.cwd():
            with Image.open(safe_path) as img:
                img.thumbnail((64, 64))
                buf = BytesIO()
                img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            thumb_html = f"<img src='data:image/png;base64,{b64}' width='50'/>"
        country = classify_image(str(safe_path))
        desc = generate_description(str(safe_path))
        rows.append([thumb_html, str(safe_path), country, "", "", desc])
    return rows
            b64 = base64.b64encode(buf.getvalue()).decode()
            thumb_html = f"<img src='data:image/png;base64,{b64}' width='50'/>"
        country = classify_image(path)
        desc = generate_description(path)
        rows.append([thumb_html, path, country, "", "", desc])
    return rows


def save_upload(preview_rows):
    if not preview_rows:
        return "❌ No rows to save"
    session = Session()
    for _, path, country, denom, year, notes in preview_rows:
        if not os.path.exists(path):
            continue
        if is_duplicate(path, session):
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
    session.commit()
    return "✅ Saved to database!"

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
for s in session.query(Stamp).all():
        thumb_html = s.image_path
        if os.path.exists(s.image_path):
            try:
                with Image.open(s.image_path) as img:
                    img.thumbnail((64, 64))
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()

                thumb = f"<img src='data:image/png;base64,{b64}' width='50'/>"
            except (IOError, OSError):
                thumb = ""  # Gracefully handle image loading errors
        else:
            thumb = ""
        data.append([thumb, s.id, s.country, s.denomination, s.year, s.notes])
    return data


def update_gallery_table(new_table):
    """Update database with inline edits."""
    session = Session()
    for row in new_table:
        thumb, stamp_id, country, denom, year, notes = row
        s = session.query(Stamp).get(int(stamp_id))
        if s:
            s.country = country
            s.denomination = denom
            s.year = year
            s.notes = notes
    session.commit()
    return "✅ Changes saved inline!"


def load_details(stamp_id):
    session = Session()
    s = session.query(Stamp).get(int(stamp_id))
    if not s:
        return "", None, "", "", "", ""
    return s.id, s.image_path, s.country, s.denomination, s.year, s.notes


def scan_and_sync_folder():
    """Scan images directory for new stamps and return metadata."""
    session = Session()
    scans = []
    for fname in os.listdir(IMAGES_DIR):
        path = os.path.join(IMAGES_DIR, fname)
        if not os.path.isfile(path):
            continue
        if session.query(Stamp).filter_by(image_path=path).first():
            continue
        country = classify_image(path)
        desc = generate_description(path)
        scans.append(
            {
                "image_path": path,
                "country": country,
                "denomination": "",
                "year": "",
                "notes": desc,
            }
        )
    return scans


def save_scans(scans):
    """Persist scan data to the database."""
    session = Session()
    for data in scans:
        stamp = Stamp(
            image_path=data["image_path"],
            country=data.get("country", ""),
            denomination=data.get("denomination", ""),
            year=data.get("year", ""),
            notes=data.get("notes", ""),
            description=data.get("notes", ""),
        )
        session.add(stamp)
}
        )
    return scans


def save_scans(scans):
    """Persist scan data to the database."""
    session = Session()
    try:
        for data in scans:
            stamp = Stamp(
                image_path=data["image_path"],
                country=data.get("country", ""),
                denomination=data.get("denomination", ""),
                year=data.get("year", ""),
                notes=data.get("notes", ""),
                description=data.get("notes", ""),
            )
            session.add(stamp)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving scans: {str(e)}")
    finally:
        session.close()


def load_gallery(_):
    """Wrapper used by tests to fetch gallery rows."""
    return load_gallery_data()
# ---------------- Export ----------------


def export_data():
    return f"📁 Exported to {export_csv()}"


# ---------------- UI ----------------
if __name__ == "__main__":
    with gr.Blocks(css="#app-container{padding:10px;}") as demo:
        gr.Markdown("# 📬 Stamp'd – Inline Editing Version")

        # --- Upload Tab ---
        with gr.Tab("➕ Upload"):
            upload_files = gr.File(


def load_gallery(_):
    """Wrapper used by tests to fetch gallery rows."""
    return load_gallery_data()
# ---------------- Export ----------------


def export_data():
    return f"📁 Exported to {export_csv()}"


# ---------------- UI ----------------
if __name__ == "__main__":
    with gr.Blocks(css="#app-container{padding:10px;}") as demo:
        gr.Markdown("# 📬 Stamp’d – Inline Editing Version")

        # --- Upload Tab ---
        with gr.Tab("➕ Upload"):
            upload_files = gr.File(
                file_types=["image"],
                file_count="multiple",
                label="Upload Stamp Images")
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
                lambda i, table: (
                    search_sources(table[int(i)][1])
                    if 0 <= int(i) < len(table)
                    else ("❌", "❌", "❌")
                ),
                [idx, preview_table],
                [ebay_iframe_u, colnect_iframe_u, hip_iframe_u],
            )

            save_status = gr.Textbox(label="Save Status")
            btn_save = gr.Button("💾 Save All")
            btn_save.click(save_upload, preview_table, save_status)

        # --- Gallery Tab ---
        with gr.Tab("📋 Gallery"):
            btn_refresh = gr.Button("🔄 Refresh")
            gallery_table = gr.Dataframe(
                headers=["Thumb", "ID", "Country", "Denom", "Year", "Notes"],
                datatype=["markdown", "number", "str", "str", "str", "str"],
                row_count="dynamic",
                interactive=True   # Enable inline editing
            )
            gallery_table.change(
                update_gallery_table,
                gallery_table,
                None)  # Auto-save on change
            btn_refresh.click(load_gallery_data, outputs=gallery_table)

            stamp_id = gr.Textbox(label="Stamp ID", interactive=False)
            image_display = gr.Image(label="Image")
            btn_rev_gallery = gr.Button("🔎 Reverse Search Selected")
            ebay_iframe_g = gr.HTML()
            colnect_iframe_g = gr.HTML()
            hip_iframe_g = gr.HTML()

            gallery_table.select(
                lambda evt: load_details(
                    evt.value[1]) if evt else (
                    "", None, "", "", "", ""), None, [
                    stamp_id, image_display, gr.Textbox(
                        visible=False), gr.Textbox(
                            visible=False), gr.Textbox(
                                visible=False), gr.Textbox(
                                    visible=False)])

            btn_rev_gallery.click(
                lambda id: search_sources(
                    Session().query(Stamp).get(
                        int(id)).image_path) if id else (
                    "❌",
                    "❌",
stamp_id, image_display, gr.Textbox(
                        visible=False), gr.Textbox(
                            visible=False), gr.Textbox(
                                visible=False), gr.Textbox(
                                    visible=False)])

            btn_rev_gallery.click(
                lambda id: search_sources_safe(id),  # Use a new function for safe searching
                inputs=stamp_id,
                outputs=[
                    ebay_iframe_g,
                    colnect_iframe_g,
                    hip_iframe_g])

        # --- Export Tab ---
        with gr.Tab("⬇️ Export"):
            btn_export = gr.Button("Export CSV")
            export_status = gr.Textbox()
            btn_export.click(export_data, outputs=export_status)

    demo.launch()

# TODO: Implement the following function in the main code
# def search_sources_safe(id):
#     try:
#         if not id:
#             return "❌", "❌", "❌"
#         stamp = Session().query(Stamp).get(int(id))
#         if not stamp or not stamp.image_path:
#             return "❌ Not found", "❌ Not found", "❌ Not found"
#         return search_sources(stamp.image_path)
#     except Exception as e:
#         print(f"Error in search_sources_safe: {e}")
#         return "❌ Error", "❌ Error", "❌ Error"
                inputs=stamp_id,
                outputs=[
                    ebay_iframe_g,
                    colnect_iframe_g,
                    hip_iframe_g])

        # --- Export Tab ---
        with gr.Tab("⬇️ Export"):
            btn_export = gr.Button("Export CSV")
            export_status = gr.Textbox()
            btn_export.click(export_data, outputs=export_status)

    demo.launch()
