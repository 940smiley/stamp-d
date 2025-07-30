import gradio as gr
import os
import requests
from bs4 import BeautifulSoup
from db import Session, Stamp
from PIL import Image
import base64
from io import BytesIO
from image_utils import enhance_and_crop, is_duplicate, classify_image
from export_utils import export_csv
from ai_utils import generate_description


# ---------------- Reverse Search ----------------
def search_relevant_sources(image_path):
    """Run refined searches for eBay sold items, Colnect, HipStamp."""
    if not image_path or not os.path.exists(image_path):
        return ("❌ Image not found.", "", "", "No match found", "")

    query = os.path.basename(image_path).replace("_", " ")

    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={query}&LH_Sold=1"
    colnect_url = f"https://colnect.com/en/stamps/list/{query}"
    hipstamp_url = (
        f"https://www.hipstamp.com/search?keywords={query}&show=store_items"
    )

    # Try to scrape top eBay match
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
        query,
    )


# ---------------- Upload + Process ----------------
def preview_upload(images):
    preview_data = []
    for img in images:
        enhance_and_crop(img)
        country = classify_image(img)
        desc = generate_description(type("StampObj", (), {"country": country, "year": "Unknown"}))
        preview_data.append([img, country, "", "", desc])
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
            description=notes,
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
        if os.path.exists(s.image_path):
            try:
                with Image.open(s.image_path) as img:
                    img.thumbnail((64, 64))
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                thumb = f"<img src='data:image/png;base64,{b64}' width='50'/>"
            except Exception:
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
with gr.Blocks() as demo:
    gr.Markdown("# 📬 Stamp’d 9.0 - Complete Manager")

    # Upload Tab
    with gr.Tab("➕ Upload Stamps"):
        images = gr.File(file_types=["image"], file_count="multiple", label="Upload Stamp Images")

        preview_table = gr.Dataframe(
            headers=["Image Path", "Country", "Denomination", "Year", "Notes"],
            datatype=["str", "str", "str", "str", "str"],
            row_count="dynamic",
        )
        images.upload(preview_upload, images, preview_table)

        idx_input = gr.Number(label="Row Index (0-based)", precision=0)
        reverse_btn_upload = gr.Button("🔎 Reverse Image Search (Selected)")

        ebay_frame = gr.HTML(visible=False)
        colnect_frame = gr.HTML(visible=False)
        hipstamp_frame = gr.HTML(visible=False)
        suggested_title = gr.Textbox(label="Top eBay Match Title", visible=False)

        # Remove components from their initial position so they can be
        # rendered later without triggering DuplicateBlockError.
        ebay_frame.unrender()
        colnect_frame.unrender()
        hipstamp_frame.unrender()
        suggested_title.unrender()

        def trigger_reverse(idx, table):
            if 0 <= int(idx) < len(table):
                ebay, colnect, hip, title, query = search_relevant_sources(table[int(idx)][0])
                return (ebay, colnect, hip, title, True, True, True, True)
            return ("❌ Invalid index", "", "", "No match", True, False, False, False)

        reverse_btn_upload.click(
            trigger_reverse,
            inputs=[idx_input, preview_table],
            outputs=[
                ebay_frame,
                colnect_frame,
                hipstamp_frame,
                suggested_title,
                ebay_frame,
                colnect_frame,
                hipstamp_frame,
                suggested_title,
            ],
        )

        with gr.Row():
            country_copy = gr.Button("📋 Copy Title → Country")
            notes_copy = gr.Button("📋 Copy Title → Notes")

        def copy_title_to_country(idx, table, title):
            idx = int(idx)
            if 0 <= idx < len(table):
                table[idx][1] = "" if title == "No match found" else title
            return table

        def copy_title_to_notes(idx, table, title):
            idx = int(idx)
            if 0 <= idx < len(table):
                table[idx][4] = "" if title == "No match found" else title
            return table

        country_copy.click(
            copy_title_to_country,
            inputs=[idx_input, preview_table, suggested_title],
            outputs=preview_table,
        )
        notes_copy.click(
            copy_title_to_notes,
            inputs=[idx_input, preview_table, suggested_title],
            outputs=preview_table,
        )

        save_status = gr.Textbox(label="Save Status")
        save_btn = gr.Button("💾 Save All")
        save_btn.click(save_upload, preview_table, save_status)

        gr.HTML("<hr/>")
        gr.Markdown("### Reverse Image Search Results")
        ebay_frame.render()
        colnect_frame.render()
        hipstamp_frame.render()
        suggested_title.render()

    # Gallery Tab
    with gr.Tab("📋 Gallery"):
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh")
            view_switch = gr.Radio(["Table View", "Images Only"], value="Table View", label="View Mode")

        gallery_table = gr.Dataframe(
            headers=["Image", "ID", "Country", "Denomination", "Year", "Notes"],
            datatype=["markdown", "number", "str", "str", "str", "str"],
            row_count="dynamic",
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

        # Prevent duplicate render errors by removing these components
        # until they are explicitly rendered later.
        ebay_frame_g.unrender()
        colnect_frame_g.unrender()
        hipstamp_frame_g.unrender()
        suggested_title_g.unrender()

        reverse_btn_gallery.click(
            lambda sid: search_relevant_sources(Session().query(Stamp).get(int(sid)).image_path) if sid else ("❌ No stamp selected", "", "", "", "", ""),
            inputs=stamp_id,
            outputs=[ebay_frame_g, colnect_frame_g, hipstamp_frame_g, suggested_title_g, gr.Textbox()],
        )

        with gr.Row():
            country_copy_g = gr.Button("📋 Copy Title → Country")
            notes_copy_g = gr.Button("📋 Copy Title → Notes")

        country_copy_g.click(copy_to_field, inputs=suggested_title_g, outputs=country_edit)
        notes_copy_g.click(copy_to_field, inputs=suggested_title_g, outputs=notes_edit)

        update_btn = gr.Button("💾 Update Stamp")
        update_btn.click(
            update_stamp_details,
            [stamp_id, country_edit, denom_edit, year_edit, notes_edit],
            update_status,
        )

        gallery_images = gr.Gallery(show_label=False, columns=5)

        def toggle_views(view_mode):
            return (
                gr.update(visible=(view_mode == "Table View")),
                gr.update(visible=(view_mode == "Images Only")),
            )

        view_switch.change(toggle_views, view_switch, [gallery_table, gallery_images])
        refresh_btn.click(load_gallery_data, outputs=gallery_table)
        refresh_btn.click(load_gallery_images, outputs=gallery_images)

        gallery_table.select(
            lambda evt: load_stamp_details(evt.value[1]),
            None,
            [stamp_id, image_display, country_edit, denom_edit, year_edit, notes_edit],
        )
        gallery_images.select(
            lambda label: load_stamp_details(label.split(":")[0].replace("ID ", "")),
            None,
            [stamp_id, image_display, country_edit, denom_edit, year_edit, notes_edit],
        )

        gr.Markdown("### Reverse Search Results")
        ebay_frame_g.render()
        colnect_frame_g.render()
        hipstamp_frame_g.render()
        suggested_title_g.render()

    # Export Tab
    with gr.Tab("⬇️ Export"):
        export_btn = gr.Button("Export CSV")
        export_status = gr.Textbox(label="Export Status")
        export_btn.click(export_data, outputs=export_status)


demo.launch()

