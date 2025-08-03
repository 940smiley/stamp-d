
# Stamp'd - Intelligent Stamp Cataloging App

Stamp'd is a powerful local-first stamp cataloging application featuring AI assistance, reverse image search, batch processing, marketplace integrations, and collection management tools.

## Features

- Upload or sync stamp images from a folder
- AI-powered image classification and description generation (configurable with Phi-3, Ollama, or LM Studio)
- Reverse image search (eBay, Colnect, Delcampe, Google Images, StampWorld)
- Inline editing and detail management per stamp
- Export capabilities (CSV, Excel, image paths)
- Gallery modes (inline spreadsheet view or image-only view)
- Auto thumbnail generation and compression
- Condition scoring, valuation, tagging, and custom fields
- Collection organization and lot assignment
- Marketplace integration (eBay, Colnect, Delcampe with API key settings)
- Full offline mode
- Auto-backup and error logging
- Customizable settings via UI toggle panel

## Getting Started

1. Clone or unzip the Stamp'd directory
2. Activate the virtual environment: `.\gradio-env\Scriptsctivate`
3. Run the app: `python app.py`
4. Access via `http://127.0.0.1:7860` in your browser

## Requirements

Install dependencies:
```
pip install -r requirements.txt
```

Ensure `stampd.db` is used as the active database.

## Notes

- Image files should be placed in the `/images` directory for folder sync.
- Set AI model preferences in the UI settings panel.
- Check the `/logs/errors.log` for error details.
