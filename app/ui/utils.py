from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative: str) -> str:
    """Путь к ресурсу: работает и из исходников, и из PyInstaller-сборки."""
    if hasattr(sys, "_MEIPASS"):
        base = Path(getattr(sys, "_MEIPASS"))
    else:
        base = Path(__file__).resolve().parents[2]
    return str(base / relative)
