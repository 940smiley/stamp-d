@echo off
title Stamp'd 2.0 Silent Mode
cd /d %~dp0
echo Activating Stamp'd silent mode...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
:: Silent mode: runs app without console output
start /min python app.py
echo Stamp'd is running in background.
exit
