@echo off
title Stamp'd 2.0 Production
cd /d %~dp0
echo Activating Stamp'd environment...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo Starting Stamp'd...
python app.py
pause
