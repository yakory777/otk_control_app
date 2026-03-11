@echo off
cd /d %~dp0
python -m pip install -r requirements.txt
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --windowed --name OTK_DXF_Inspector --add-data "data;data" main.py
pause
