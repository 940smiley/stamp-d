import config
import os
import requests
import re
import random
from db import Session, Stamp

# Optional: integrate Ollama / LM Studio if available
USE_OLLAMA = True
OLLAMA_MODEL = "llava-phi3"
LM_STUDIO_API = "http://127.0.0.1:1234/v1/completions"

# -------------------------
# AI Utility Functions
# -------------------------

def query_ollama(prompt: str) -> str:
    """Query local Ollama model for metadata suggestion."""
    try:
        import subprocess, json
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )
        output = result.stdout.decode().strip()
        return output if output else "Unknown"
    except Exception:
        return None

def query_lm_studio(prompt: str) -> str:
    """Query LM Studio if running locally."""
    try:
        r = requests.post(
            LM_STUDIO_API,
            headers={"Content-Type": "application/json"},
            json={"prompt": prompt, "max_tokens": 200},
            timeout=20
        )
        if r.status_code == 200:
            return r.json().get("choices", [{}])[0].get("text", "").strip()
        return None
    except Exception:
        return None

def generate_metadata(image_path: str) -> dict:
    """
    Generate metadata for a stamp using local AI if available,
    otherwise fall back to dummy values.
    """
    prompt = f"Identify the country, year, color, and format of this stamp: {os.path.basename(image_path)}"
    response = query_ollama(prompt) or query_lm_studio(prompt)
    if not response:
        # Fallback dummy
        return {
            "country": "Unknown",
            "year": "",
            "format": "Single",
            "description": f"Stamp from image {os.path.basename(image_path)}"
        }

    # Basic parsing
    metadata = {
        "country": "Unknown",
        "year": "",
        "format": "Single",
        "description": response
    }
    # Simple regex extraction
    year_match = re.search(r"(18|19|20)\d{2}", response)
    if year_match:
        metadata["year"] = year_match.group(0)
    for word in ["USA", "Germany", "France", "UK", "Canada", "Japan", "Italy"]:
        if word.lower() in response.lower():
            metadata["country"] = word
            break
    return metadata

def auto_fill_blank_fields():
    """Fill blank metadata fields for all stamps."""
    session = Session()
    stamps = session.query(Stamp).all()
    for s in stamps:
        if not s.country or not s.year or not s.description:
            md = generate_metadata(s.image_path)
            if not s.country:
                s.country = md["country"]
            if not s.year:
                s.year = md["year"]
            if not s.description:
                s.description = md["description"]
    session.commit()

def assign_lots_ai():
    """Auto-assign lot numbers and optional collection if missing."""
    session = Session()
    stamps = session.query(Stamp).all()
    lot_counter = 1
    for s in stamps:
        if not s.lot_number:
            s.lot_number = f"L{lot_counter:04d}"
            lot_counter += 1
        if not s.collection:
            # Simple heuristic based on country
            s.collection = s.country or "General Collection"
    session.commit()

def suggest_price_ai():
    """
    Suggest prices based on dummy logic.
    Real implementation would scrape eBay / HipStamp / Delcampe sold listings.
    """
    session = Session()
    stamps = session.query(Stamp).all()
    for s in stamps:
        if not s.price or s.price == 0:
            # Simple heuristic: random 1-20 USD for demo
            s.price = round(random.uniform(1, 20), 2)
    session.commit()
    return "✅ Price suggestion complete"
