# tests/test_config_service.py

from __future__ import annotations

import tempfile
from pathlib import Path

from app.domain.models import AppConfig
from app.services.config_service import ConfigService


def test_load_missing_returns_defaults():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "nonexistent.json"
        svc = ConfigService(str(path))
        cfg = svc.load()
        assert cfg.data_dir == "data"
        assert cfg.operator == ""
        assert cfg.theme == "light"


def test_save_and_load():
    with tempfile.NamedTemporaryFile(
        suffix=".json",
        delete=False,
    ) as f:
        path = f.name
    try:
        svc = ConfigService(path)
        cfg = AppConfig(
            data_dir="test_data",
            operator="Иванов",
            theme="dark",
            db_path="data/otk.db",
        )
        svc.save(cfg)
        loaded = svc.load()
        assert loaded.data_dir == "test_data"
        assert loaded.operator == "Иванов"
        assert loaded.theme == "dark"
    finally:
        Path(path).unlink(missing_ok=True)
