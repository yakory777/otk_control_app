"""
Сборка exe через PyInstaller. Имя и версия берутся из pyproject.toml.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _parse_version(version: str) -> tuple[int, int, int, int]:
    """Преобразует строку версии в кортеж из 4 int (filevers/prodvers)."""
    parts = re.split(r"[-.]", version.strip())[:4]
    out: list[int] = []
    for p in parts:
        try:
            out.append(int(p))
        except ValueError:
            out.append(0)
    while len(out) < 4:
        out.append(0)
    return (out[0], out[1], out[2], out[3])


def _load_pyproject(project_root: Path) -> dict:
    with open(project_root / "pyproject.toml", "rb") as f:
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore[no-redef]
        return tomllib.load(f)


def _write_version_file(
    path: Path,
    version_tuple: tuple[int, int, int, int],
    version_str: str,
    product_name: str,
    description: str,
) -> None:
    """Пишет version-info файл для Windows (формат PyInstaller)."""
    from PyInstaller.utils.win32.versioninfo import (  # type: ignore[import-untyped]
        FixedFileInfo,
        StringFileInfo,
        StringStruct,
        StringTable,
        VarFileInfo,
        VarStruct,
        VSVersionInfo,
    )

    ffi = FixedFileInfo(
        filevers=version_tuple,
        prodvers=version_tuple,
        mask=0x3F,
        flags=0x0,
        OS=0x4,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0),
    )
    st = StringTable(
        "040904B0",
        [
            StringStruct("CompanyName", ""),
            StringStruct("FileDescription", description),
            StringStruct("FileVersion", version_str),
            StringStruct("InternalName", product_name),
            StringStruct("LegalCopyright", ""),
            StringStruct("OriginalFilename", product_name + ".exe"),
            StringStruct("ProductName", product_name),
            StringStruct("ProductVersion", version_str),
        ],
    )
    sfi = StringFileInfo([st])
    vfi = VarFileInfo([VarStruct("Translation", [1033, 1200])])
    info = VSVersionInfo(ffi=ffi, kids=[sfi, vfi])
    path.write_text(str(info), encoding="utf-8")


def _clean_dist_dir(root: Path, exe_name: str) -> bool:
    """
    Очищает dist/<exe_name> перед сборкой. Возвращает False при блокировке.
    """
    dist_dir = root / "dist" / exe_name
    if not dist_dir.exists():
        return True
    try:
        shutil.rmtree(dist_dir)
        return True
    except PermissionError:
        print(
            f"\nОшибка: папка {dist_dir} занята (exe запущен или открыт в проводнике).\n"
            f"Закройте {exe_name}.exe и папку dist, затем повторите сборку.\n",
            file=sys.stderr,
        )
        return False


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    os.chdir(root)

    data = _load_pyproject(root)
    project = data["project"]
    version_str = project["version"]
    version_tuple = _parse_version(version_str)
    exe_name = (
        data.get("tool", {}).get("pyinstaller", {}).get("name")
        or project["name"].replace("-", "_")
    )
    description = project.get("description", exe_name)

    version_file = root / "version_info.txt"
    _write_version_file(
        version_file,
        version_tuple,
        version_str,
        exe_name,
        description,
    )

    if not _clean_dist_dir(root, exe_name):
        return 1

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--name",
        exe_name,
        "--version-file",
        str(version_file),
        "--add-data",
        "data;data",
        "main.py",
    ]
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
