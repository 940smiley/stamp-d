import gradio as gr
import os, requests, base64
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from db import Session, Stamp
from image_utils import enhance_and_crop, is_duplicate, classify_image
from export_utils import export_csv
from ai_utils import generate_description

# ---------------- Reverse Search ----------------
def search_relevant_sources(image_path):
    """Return three embedded search iframes for eBay sold, Colnect, HipStamp."""
    if not image_path or not os.path.exists(image_path):
        err = "❌ Image not found."
        return err, err, err

    q = os.path.basename(image_path).replace("_", " ")
    ebay = f"https://www.ebay.com/sch/i.html?_nkw={q}&LH_Sold=1"
    colnect = f"https://colnect.com/en/stamps/list/{q}"
    hip = f"https://www.hipstamp.com/search?keywords={q}&show=store_items"

    return (
        f'<iframe src="{ebay}" width="100%" height="300"></iframe>',
        f'<iframe src="{colnect}" width="100%" height="300"></iframe>',
        f'<iframe src="{hip}" width="100%" height="300"></iframe>'
    )

# ---------------- Upload / Preview ----------------
def preview_upload(images):
    """Generate thumbnail + OCR/AI predictions for preview table."""
    rows = []
    for path in images:
        # thumbnail
        thumb = path
        if os.path.exists(path):
            try:
                with Image.open(path) as img:
                    img.thumbnail((64,64))
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                thumb = f"<img src='data:image/png;base64,{b64}' width='50'/>"
            except:
                pass

        country = classify_image(path)
        desc = generate_description(type("S",( ),{"country":country,"year":"Unknown"}))
        # columns: thumbnail, path, country, denom, year, notes
        rows.append([thumb, path, country, "", "", desc])
    return rows

def save_upload(preview_table):
    """Persist preview rows into the database."""
    sess = Session()
    for thumb, path, country, denom, year, notes in preview_table:
        if not os.path.exists(path): continue
        if is_duplicate(path, sess): continue
        s = Stamp(
            country=country,
            denomination=denom,
            year=year,
            notes=notes,
            image_path=path,
            description=notes
        )
        sess.add(s)
    sess.commit()
    return "✅ Saved!"

# ---------------- Gallery ----------------
def load_gallery_data():
    """Load all stamps as rows with thumbnails."""
    sess = Session()
    out = []
    for s in sess.query(Stamp).all():
        thumb = s.image_path
        if os.path.exists(s.image_path):
            try:
                with Image.open(s.image_path) as img:
                    img.thumbnail((64,64))
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                thumb = f"<img src='data:image/png;base64,{b64}' width='50'/>"
            except:
                pass
        out.append([thumb, s.id, s.country, s.denomination, s.year, s.notes])
    return out

def load_stamp_details(stamp_id):
    """Fetch a single stamp’s details for editing."""
    sess = Session()
    s = sess.query(Stamp).get(int(stamp_id))
    if not s:
        return "", None, "", "", "", ""
    return s.id, s.image_path, s.country, s.denomination, s.year, s.notes

def update_stamp_details(stamp_id, country, denom, year, notes):
    """Persist edits to a stamp."""
    sess = Session()
    s = sess.query(Stamp).get(int(stamp_id))
    if not s:
        return "❌ Not found"
    s.country, s.denomination, s.year, s.notes = country, denom, year, notes
    sess.commit()
    return f"✅ Updated ID {stamp_id}"

# ---------------- Export ----------------
def export_data():
    return f"📁 {export_csv()}"

# ---------------- UI ----------------
with gr.Blocks(css="#app-container{padding:10px;}") as demo:
    gr.Markdown("# 📬 Stamp’d – Simplified & Stable")

    # --- Upload Tab ---
    with gr.Tab("➕ Upload"):
        imgs = gr.File(file_types=["image"], file_count="multiple")
        preview = gr.Dataframe(
            headers=["Thumb","Path","Country","Denom","Year","Notes"],
            datatype=["markdown","str","str","str","str","str"],
            row_count="dynamic"
        )
        status_save = gr.Textbox(label="Save Status")

        # Reverse search frames
        idx = gr.Number(label="Index (0-based)", precision=0)
        btn_rev = gr.Button("🔎 Reverse Search")
        ebay_iframe = gr.HTML()
        colnect_iframe = gr.HTML()
        hip_iframe = gr.HTML()

        imgs.upload(preview_upload, imgs, preview)
        btn_rev.click(
            lambda i, tbl: search_relevant_sources(tbl[int(i)][1]) if 0<=int(i)<len(tbl) else ("❌","❌","❌"),
            inputs=[idx, preview],
            outputs=[ebay_iframe, colnect_iframe, hip_iframe]
        )

        gr.Row([ebay_iframe, colnect_iframe, hip_iframe])

        gr.Row([gr.Button("💾 Save All")
                .click(save_upload, preview, status_save), status_save])

    # --- Gallery Tab ---
    with gr.Tab("📋 Gallery"):
        btn_ref = gr.Button("🔄 Refresh")
        table = gr.Dataframe(
            headers=["Thumb","ID","Country","Denom","Year","Notes"],
            datatype=["markdown","number","str","str","str","str"],
            row_count="dynamic"
        )
        sid = gr.Textbox(label="Stamp ID", interactive=False)
        img_disp = gr.Image(label="Image")
        fld_country = gr.Textbox(label="Country")
        fld_denom = gr.Textbox(label="Denomination")
        fld_year = gr.Textbox(label="Year")
        fld_notes = gr.Textbox(label="Notes", lines=3)
        status_upd = gr.Textbox(label="Update Status")
        btn_upd = gr.Button("💾 Update")
        btn_rev_g = gr.Button("🔎 Reverse Search")
        ebay_iframe_g = gr.HTML()
        colnect_iframe_g = gr.HTML()
        hip_iframe_g = gr.HTML()

        btn_ref.click(load_gallery_data, outputs=table)
        table.select(
            lambda evt: load_stamp_details(evt.value[1]) if evt else ("",None,"","","",""),
            None,
            [sid, img_disp, fld_country, fld_denom, fld_year, fld_notes]
        )
        btn_upd.click(
            update_stamp_details,
            [sid, fld_country, fld_denom, fld_year, fld_notes],
            status_upd
        )
        btn_rev_g.click(
            lambda id: search_relevant_sources(Session().query(Stamp).get(int(id)).image_path) if id else ("❌","❌","❌"),
            inputs=sid,
            outputs=[ebay_iframe_g, colnect_iframe_g, hip_iframe_g]
        )

        gr.Row([ebay_iframe_g, colnect_iframe_g, hip_iframe_g])
        gr.Row([btn_ref, table])
        gr.Row([sid, img_disp])
        gr.Row([fld_country, fld_denom, fld_year])
        gr.Row([fld_notes])
        gr.Row([btn_upd, status_upd, btn_rev_g])

    # --- Export Tab ---
    with gr.Tab("⬇️ Export"):
        btn_exp = gr.Button("Export CSV")
        out_exp = gr.Textbox(label="Export Status")
        btn_exp.click(export_data, outputs=out_exp)

demo.launch()
