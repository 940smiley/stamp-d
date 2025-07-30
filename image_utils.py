import cv2
import imagehash
from PIL import Image, ImageEnhance
import numpy as np
import os
from sqlalchemy.orm import Session
from db import Stamp

def enhance_and_crop(image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)
    # Auto-crop whitespace
    open_cv_img = np.array(img)
    gray = cv2.cvtColor(open_cv_img, cv2.COLOR_BGR2GRAY)
    coords = cv2.findNonZero(255 - gray)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        img = img.crop((x, y, x + w, y + h))
    img.save(image_path)
    return image_path

def is_duplicate(image_path, db_session: Session):
    current_hash = imagehash.phash(Image.open(image_path))
    for stamp in db_session.query(Stamp).all():
        if os.path.exists(stamp.image_path):
            hash_existing = imagehash.phash(Image.open(stamp.image_path))
            if abs(current_hash - hash_existing) < 5:
                return True
    return False

def classify_image(image_path):
    # Placeholder: CLIP model or ML classifier
    return "Predicted Country"
