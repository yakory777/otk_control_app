# tests/test_dxf_parser.py

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.dxf_parser import DxfParser


def test_parse_file_empty_or_missing():
    parser = DxfParser()
    # Несуществующий файл — парсер может выбросить или вернуть []
    path = Path(__file__).parent.parent / "data" / "examples"
    if not path.exists():
        pytest.skip("data/examples отсутствует")
    nonexistent = path / "nonexistent_12345.dxf"
    if nonexistent.exists():
        nonexistent = path / "really_nonexistent.dxf"
    try:
        result = parser.parse_file(str(nonexistent))
        assert result == []
    except (FileNotFoundError, OSError):
        pass


def test_parse_file_returns_list():
    path = Path(__file__).parent.parent / "data" / "examples"
    if not path.exists():
        pytest.skip("data/examples отсутствует")
    dxf_files = list(path.glob("*.dxf"))
    if not dxf_files:
        pytest.skip("Нет DXF в data/examples")
    parser = DxfParser()
    result = parser.parse_file(str(dxf_files[0]))
    assert isinstance(result, list)


def test_find_nearest_empty():
    parser = DxfParser()
    entities = []
    assert parser.find_nearest(entities, 0, 0) is None
