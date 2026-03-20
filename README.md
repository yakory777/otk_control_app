# otk-control-app

Приложение для просмотра DXF-файлов и аналитики (превью, контрольные точки ОТК).

## Запуск

```bash
python main.py
```

## Зависимости

Указаны в `pyproject.toml`. Установка: `poetry install` или `uv sync`.

## Сборка exe (Windows)

Имя exe и версия берутся из `pyproject.toml` (поля `project.name` / `project.version` и при необходимости `tool.pyinstaller.name`). Версия попадает в метаданные exe (свойства файла в Windows).

Установить зависимости с dev-группой (в т.ч. PyInstaller):

```bash
poetry install --with dev
```

Сборка одной командой:

```bash
poetry run python scripts/build_exe.py
```

Или запустить `build_windows_exe.bat` — он сам выполнит установку и сборку.

Готовый exe: `dist/<имя>/<имя>.exe` (имя задаётся в `tool.pyinstaller.name` или из `project.name`).
