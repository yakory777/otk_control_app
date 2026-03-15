# app/services/history_service.py

from __future__ import annotations

import logging
from typing import Optional, cast

from app.domain.models import HistoryEntry

logger = logging.getLogger(__name__)


class HistoryService:
    """Сервис записи и чтения истории изменений по проектам."""

    def __init__(self, repo) -> None:
        self._repo = repo

    def log(
        self,
        project_id: int,
        operator: str,
        action: str,
        point_number: Optional[int],
        old_value: Optional[str],
        new_value: Optional[str],
    ) -> None:
        self._repo.log(
            project_id, operator, action,
            point_number, old_value, new_value,
        )

    def get_history(self, project_id: int) -> list[HistoryEntry]:
        return cast(list[HistoryEntry], self._repo.get_history(project_id))
