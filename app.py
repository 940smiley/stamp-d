import os
import requests
from PIL import Image
import gradio as gr
from config import IMAGES_DIR, TINEYE_API_URL, TINEYE_API_KEY
from db import Session, Stamp
from image_utils import enhance_and_crop
from ai_utils import generate_description

def save_image(file, upload_dir=IMAGES_DIR):
    filename = os.path.join(upload_dir, os.path.basename(file.name))
    file.save(filename)
    return filename

def reverse_image_lookup(image_path):
    if not image_path or not os.path.exists(image_path):
        return "❌ No valid image found."

    # Primary: TinEye reverse image search
    try:
        with open(image_path, "rb") as image_file:
            response = requests.post(
                TINEYE_API_URL,
                auth=(TINEYE_API_KEY, ""),
                files={"image": image_file}
            )
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                return results
    except Exception as e:
        print(f"Tineye lookup failed: {e}")

    # Fallback: Google Images reverse search
    try:
        encoded_filename = os.path.basename(image_path).replace(" ", "+")
        fallback_url = f"https://images.google.com/searchbyimage?image_url={encoded_filename}"
        return f"🔍 No TinEye match. Try Google Images:\n{fallback_url}"
    except Exception as e:
        return f"⚠️ Reverse lookup failed: {str(e)}"

def enhance_and_classify(file):
    image_path = save_image(file)
    enhanced_path = enhance_and_crop(image_path)
    description = generate_description(enhanced_path)
    reverse_results = reverse_image_lookup(enhanced_path)
    return enhanced_path, description, reverse_results

def toggle_views(view_mode):
    return (
        gr.update(visible=(view_mode == "Table View")),
        gr.update(visible=(view_mode == "Images Only"))
    )

with gr.Blocks(title="Stamp’d") as demo:
    with gr.Tab("🔍 Reverse Lookup"):
        file_input = gr.File(label="Upload Stamp")
        image_output = gr.Image()
        description_output = gr.Textbox(label="AI Description")
        results_output = gr.Textbox(label="Reverse Image Results")

        file_input.change(
            enhance_and_classify,
            inputs=file_input,
            outputs=[image_output, description_output, results_output]
        )

    with gr.Tab("📋 Gallery"):
        stamp_id = gr.Textbox(label="Stamp ID")
        reverse_btn_gallery = gr.Button("🔎 Gallery Reverse Search")
        ebay_frame_g = gr.Textbox()
        colnect_frame_g = gr.Textbox()
        hipstamp_frame_g = gr.Textbox()
        suggested_title_g = gr.Textbox()
        country_edit = gr.Textbox(label="Country")
        denom_edit = gr.Textbox(label="Denomination")
        year_edit = gr.Textbox(label="Year")
        notes_edit = gr.Textbox(label="Notes")
        update_status = gr.Textbox()

        def gallery_reverse_search(stamp_id):
            # Placeholder lookup for now
            return ("eBay result", "Colnect result", "HipStamp result", "Suggested title", "US", "5¢", "1950")

        def update_stamp_details(stamp_id, country, denom, year, notes):
            # Placeholder update logic
            return f"✅ Updated {stamp_id} with new details."

        reverse_btn_gallery.click(
            gallery_reverse_search,
            inputs=stamp_id,
            outputs=[ebay_frame_g, colnect_frame_g, hipstamp_frame_g, suggested_title_g, country_edit, denom_edit, year_edit]
        )

        update_btn = gr.Button("💾 Update Stamp")
        update_btn.click(
            update_stamp_details,
            inputs=[stamp_id, country_edit, denom_edit, year_edit, notes_edit],
            outputs=update_status
        )

if __name__ == "__main__":
    demo.launch()
