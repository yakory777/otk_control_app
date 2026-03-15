# app/services/config_service.py

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.domain.models import AppConfig

logger = logging.getLogger(__name__)


class ConfigService:
    """Сервис загрузки и сохранения конфигурации приложения."""

    def __init__(self, config_path: str = "config.json") -> None:
        self._path = Path(config_path)

    def load(self) -> AppConfig:
        """Загрузить конфигурацию из файла или вернуть defaults."""
        if not self._path.exists():
            return AppConfig()
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return AppConfig(
                data_dir=data.get("data_dir", "data"),
                operator=data.get("operator", ""),
                theme=data.get("theme", "light"),
                db_path=data.get("db_path", "data/otk.db"),
            )
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Не удалось загрузить конфиг %s: %s", self._path, e)
            return AppConfig()

    def save(self, config: AppConfig) -> None:
        """Сохранить конфигурацию в файл."""
        data = {
            "data_dir": config.data_dir,
            "operator": config.operator,
            "theme": config.theme,
            "db_path": config.db_path,
        }
        try:
            self._path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.debug("Конфигурация сохранена: %s", self._path)
        except OSError as e:
            logger.exception("Ошибка сохранения конфига: %s", e)
