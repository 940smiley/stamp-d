import subprocess, sys

modules = [
    "gradio", "sqlalchemy", "psycopg2-binary", "pandas", "pillow", "opencv-python",
    "imagehash", "plotly", "pyzbar", "qrcode", "flask-login", "scikit-image",
    "requests", "beautifulsoup4", "reportlab", "pyinstaller"
]

for m in modules:
    subprocess.check_call([sys.executable, "-m", "pip", "install", m])

print("✅ Stamp’d environment ready. Run `python -m stampd.app` to start.")
