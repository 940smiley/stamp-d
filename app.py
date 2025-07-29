import gradio as gr
from db import Session, Stamp
from image_utils import enhance_and_crop, is_duplicate, classify_image
from export_utils import export_csv
from ai_utils import generate_description
from PIL import Image
import os

# ---------------- Upload + Process ----------------
def preview_upload(images):
    """Process uploaded images and return preview data for editing"""
    preview_data = []
    for img in images:
        enhance_and_crop(img)
        country = classify_image(img)
        desc = generate_description(type("StampObj", (), {"country": country, "year": "Unknown"}))
        preview_data.append([img, country, "", "", desc])
    return preview_data

def save_upload(preview_table):
    """Save edited stamps from preview table"""
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
    """Load stamps for table view"""
    session = Session()
    stamps = session.query(Stamp).all()
    data = []
    for s in stamps:
        thumb = s.image_path if os.path.exists(s.image_path) else ""
        data.append([thumb, s.id, s.country, s.denomination, s.year, s.notes])
    return data

def load_gallery_images():
    """Return images only for grid view"""
    session = Session()
    stamps = session.query(Stamp).all()
    return [(s.image_path, f"ID {s.id}: {s.country}") for s in stamps]

def load_stamp_details(stamp_id):
    """Load a single stamp details for editing"""
    session = Session()
    s = session.query(Stamp).get(int(stamp_id))
    if s:
        return s.id, s.image_path, s.country, s.denomination, s.year, s.notes
    return "", "", "", "", "", ""

def update_stamp_details(stamp_id, country, denomination, year, notes):
    """Update details for a single stamp"""
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
    gr.Markdown("# 📬 Stamp’d 5.0 - Full Manager")

    # Upload Tab
    with gr.Tab("➕ Upload Stamps"):
        images = gr.File(file_types=["image"], file_count="multiple", label="Upload Stamp Images")
        preview_table = gr.Dataframe(
            headers=["Image Path", "Country", "Denomination", "Year", "Notes"],
            datatype=["str", "str", "str", "str", "str"],
            row_count=3
        )
        save_status = gr.Textbox(label="Save Status")
        images.upload(preview_upload, images, preview_table)
        save_btn = gr.Button("Save All")
        save_btn.click(save_upload, preview_table, save_status)

    # Gallery Tab
    with gr.Tab("📋 Gallery"):
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh")
            view_switch = gr.Radio(["Table View", "Images Only"], value="Table View", label="View Mode")
        
        # Table View
        gallery_table = gr.Dataframe(
            headers=["Image", "ID", "Country", "Denomination", "Year", "Notes"],
            datatype=["str", "number", "str", "str", "str", "str"],
            row_count=5
        )
        stamp_id = gr.Textbox(label="Stamp ID", interactive=False)
        image_display = gr.Image(label="Stamp Image")
        country = gr.Textbox(label="Country")
        denom = gr.Textbox(label="Denomination")
        year = gr.Textbox(label="Year")
        notes = gr.Textbox(label="Notes", lines=3)
        update_status = gr.Textbox(label="Update Status")
        update_btn = gr.Button("Update Stamp")

        # Images Only Gallery
        gallery_images = gr.Gallery(show_label=False, columns=5, elem_id="gallery_images")

        # Switch between views
        def toggle_views(view_mode):
            return (gr.update(visible=(view_mode=="Table View")),
                    gr.update(visible=(view_mode=="Images Only")))

        view_switch.change(toggle_views, view_switch, [gallery_table, gallery_images])

        # Refresh both views
        refresh_btn.click(load_gallery_data, outputs=gallery_table)
        refresh_btn.click(load_gallery_images, outputs=gallery_images)

        # Click on table row to edit
        gallery_table.select(
            lambda evt: load_stamp_details(evt.value[1]), # ID column
            None,
            [stamp_id, image_display, country, denom, year, notes]
        )
        update_btn.click(
            update_stamp_details,
            [stamp_id, country, denom, year, notes],
            update_status
        )

        # Click on image in gallery to edit (same modal)
        gallery_images.select(
            lambda label: load_stamp_details(label.split(":")[0].replace("ID ","")),
            None,
            [stamp_id, image_display, country, denom, year, notes]
        )

    # Export Tab
    with gr.Tab("⬇️ Export"):
        export_btn = gr.Button("Export CSV")
        export_status = gr.Textbox(label="Export Status")
        export_btn.click(export_data, outputs=export_status)

demo.launch()
