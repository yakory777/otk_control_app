@echo off
cd /d %~dp0
poetry install --with dev
poetry run python scripts\build_exe.py
pause
