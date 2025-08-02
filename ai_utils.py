"""AI helpers for Stamp'd.

The functions in this module provide a thin wrapper around local models
exposed by [Ollama](https://github.com/ollama/ollama).  The vision
endpoint is used when available; otherwise, simple heuristic metadata is
returned.  The goal is to keep the functions resilient so that tests can
run in environments where the model server is not present.
"""

from __future__ import annotations

import base64
import os
import re
from typing import Dict

import requests

from config import CONFIG

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


def _query_ollama_vision(image_path: str, prompt: str) -> str | None:
    """Send *image_path* to the local Ollama vision endpoint.

    Returns the textual response or ``None`` if the request fails.
    """
    try:
Returns the textual response or ``None`` if the request fails.
    """
    try:
        # import os.path
        # Use os.path.abspath and os.path.join to create a safe, absolute file path
        safe_path = os.path.abspath(os.path.join(os.path.dirname(__file__), image_path))
        if not safe_path.startswith(os.path.dirname(__file__)):
            return None  # Path is outside the allowed directory
        with open(safe_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        payload = {
            "model": CONFIG.get("ai_model", "phi3"),
            b64 = base64.b64encode(f.read()).decode()
        payload = {
            "model": CONFIG.get("ai_model", "phi3"),
            "prompt": prompt,
            "images": [b64],
        }
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception:
        pass
    return None


def generate_metadata(image_path: str) -> Dict[str, str]:
    """Return a dictionary with AI generated metadata for *image_path*.

    The function attempts to query Ollama.  If the model is unavailable a
    deterministic fallback is returned so that unit tests can run without
    external dependencies.
    """
    prompt = "Identify the stamp's country and denomination"
    response = _query_ollama_vision(image_path, prompt)
    if not response:
        # Fallback deterministic values based on file name to make tests stable
        name = os.path.splitext(os.path.basename(image_path))[0]
        return {
            "name": name,
            "country": "Unknown",
            "denomination": "",
            "description": f"Stamp from {name}",
        }

    metadata = {
        "name": "",
        "country": "Unknown",
        "denomination": "",
        "description": response,
    }
    m = re.search(r"(18|19|20)\d{2}", response)
    if m:
        metadata["year"] = m.group(0)
    for word in ["USA", "Germany", "France", "UK", "Canada", "Japan", "Italy"]:
        if word.lower() in response.lower():
            metadata["country"] = word
            break
    return metadata
