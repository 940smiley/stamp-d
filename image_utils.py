import os
import hashlib
from PIL import Image, ImageDraw, ImageFont

IMAGE_FOLDER = "images"
TEMP_UPLOADS = "temp_uploads"
THUMB_SIZE = (96, 96)
LISTING_MAX_SIZE = (1600, 1600)  # Resize for eBay/Delcampe
WATERMARK_TEXT = "Recovered Treasures"
WATERMARK_ENABLED = True

os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(TEMP_UPLOADS, exist_ok=True)

# -------------------------
# Duplicate Detection
# -------------------------


def get_file_hash(filepath):
    """Return MD5 hash for duplicate detection."""
    if not os.path.exists(filepath):
        return None
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def is_duplicate(filepath, existing_hashes):
    """Check if file hash exists in DB hash list."""
    file_hash = get_file_hash(filepath)
    return file_hash in existing_hashes


# -------------------------
# Thumbnail Generation
# -------------------------


def generate_thumbnail(image_path):
    """Generate HTML thumbnail for Gradio gallery table."""
    if not os.path.exists(image_path):
        return ""
    try:
        img = Image.open(image_path)
        img.thumbnail(THUMB_SIZE)
        thumb_path = os.path.join(
            TEMP_UPLOADS, f"thumb_{os.path.basename(image_path)}"
        )
        img.save(thumb_path)
        return f"<img src='{thumb_path}' width='50'/>"
    except Exception:
        return ""


# -------------------------
# Image Processing for Listings
# -------------------------


def resize_for_listing(image_path, watermark=WATERMARK_ENABLED):
    """Resize image and apply optional watermark for marketplace listing."""
    if not os.path.exists(image_path):
        return None

    try:
        img = Image.open(image_path).convert("RGBA")
        img.thumbnail(LISTING_MAX_SIZE)

        if watermark:
            txt = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt)
            font_size = int(img.size[0] / 20)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()
            text_width, text_height = draw.textsize(WATERMARK_TEXT, font)
            position = (
                img.size[0] - text_width - 10,
                img.size[1] - text_height - 10,
            )
            draw.text(
                position,
                WATERMARK_TEXT,
                fill=(255, 255, 255, 128),
                font=font,
            )
            img = Image.alpha_composite(img, txt)

        out_path = os.path.join(
            TEMP_UPLOADS, f"listing_{os.path.basename(image_path)}"
        )
        img.convert("RGB").save(out_path, "JPEG", quality=85)
        return out_path

    except Exception as e:
        print(f"❌ Error processing image {image_path}: {e}")
        return None


# -------------------------
# Folder Scanning
# -------------------------


def process_new_images():
    """Scan image folder for new images and return list of paths."""
    files = []
    for fname in os.listdir(IMAGE_FOLDER):
        if fname.lower().endswith((".jpg", ".jpeg", ".png")):
            files.append(os.path.join(IMAGE_FOLDER, fname))
    return files
