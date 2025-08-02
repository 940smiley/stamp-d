
# 📦 Stamp’d - Quick Start Guide

## 🚀 Overview
Stamp’d is a production-ready, AI-powered stamp cataloging and inventory management app designed for collectors, dealers, and archivists. It supports:
- Batch and single stamp uploads
- AI classification and description
- Reverse image search
- Inline editing and smart fields
- eBay/Colnect/Delcampe integration (configurable)
- Full offline mode (if desired)
- LLM support via Ollama + LM Studio fallback

## 🖥️ System Requirements
- Python 3.10+ (recommended: 3.11)
- Windows 10 or higher / Linux / macOS
- Local LLMs via [Ollama](https://ollama.com/) (e.g. `phi3`, `mistral`, `llama3`)
- Optional: LM Studio (fallback AI agent)
- Minimum 8GB RAM (16GB+ recommended for 13B models)

## 🔧 Installation

### 1. Clone/Unzip
Extract the provided `stamp-d.zip` into a folder (e.g. `G:\stamp-d`).

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/macOS
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Install LLMs via Ollama
```bash
ollama run phi3
# Optional:
ollama run llama3
```

### 5. Start the App
```bash
python app.py
```

## 📁 Folder Structure

```
stamp-d/
│
├── app.py
├── db.py
├── export_utils.py
├── settings.py
├── templates/
├── static/
├── stampd_production_ready/
│   ├── images/
│   ├── thumbnails/
│   └── backups/
├── stampd.db
├── requirements.txt
└── QUICK_START_GUIDE.md
```

## ✅ Basic Usage

### 🖼️ Uploading Stamps
- Use the "Upload" tab to add new stamps manually.
- Use the “Sync & Auto-Fill” button to scan `/images/` folder and auto-populate DB.

### ✏️ Editing Stamps
- Use the **Inline Gallery** to edit stamps directly.
- Click any **row** to load that stamp’s full details.
- Use **Save/Update** button to commit edits.

### 🔎 Reverse Image Search
- Click "Reverse Image Search" on uploaded stamps.
- Tabs: Google, eBay, Colnect, Delcampe, StampWorld
- Embedded “Copy” buttons to transfer data

## 🧠 AI Features

- **Auto Classify Image** → Categorizes stamp country/type
- **Generate Description** → Writes a natural description
- AI powered by **Ollama (default: phi3)** or **LM Studio fallback**
- Customize model in Settings

## ⚙️ Settings Tab

- Enable/Disable: auto backup, thumbnail compression, silent mode
- Configure:
  - Ollama model name
  - Reverse search providers
  - API keys
  - Marketplace login info

## 📤 Exporting & Backup

- Manual export:
  - **CSV**
  - **XLSX**
  - **PDF**
- Export image paths only
- Auto backup hourly

## 🛒 Marketplace Integration (WIP)

- eBay, Colnect, Delcampe tabs
- Assign price, listing URL, status
- Mark items as Sold
- Assign/change Lot #
- AI Lot Assignment (beta)

## 💡 Tips

- Add images to `/stampd_production_ready/images` to auto scan
- Use “Refresh Gallery” after Sync
- Inline edits save on Update
- See "Error Logs" tab for debug info

## 🧠 Recommended Ollama Models

| Model      | VRAM Needed | Performance    | Notes                       |
|------------|-------------|----------------|-----------------------------|
| `phi3`     | ~4-6GB      | Fast, compact   | Default                     |
| `llama3`   | ~10-12GB    | More powerful   | Use if GPU has enough VRAM |
| `mistral`  | ~7-8GB      | Balanced        | Good fallback              |

## 📚 Troubleshooting

- **Sync shows nothing?** → Check `/images/` has `.png`, `.jpg`
- **No thumbnails?** → Rebuild in Settings
- **Reverse Image Search fails?** → Ensure default browser is active

## 🔐 Security & Privacy

- All data local
- Offline-capable
- LLMs local via Ollama or LM Studio
