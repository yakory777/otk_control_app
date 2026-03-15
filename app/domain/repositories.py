# app/domain/repositories.py

from __future__ import annotations

from typing import Optional, Protocol

from app.domain.models import HistoryEntry, Project


class IProjectRepository(Protocol):
    def list_all(self) -> list[Project]: ...
    def get_by_id(self, project_id: int) -> Optional[Project]: ...
    def add(self, project: Project) -> None: ...
    def update(self, project: Project) -> None: ...
    def remove(self, project_id: int) -> None: ...
    def next_id(self) -> int: ...


class IHistoryRepository(Protocol):
    def log(
        self,
        project_id: int,
        operator: str,
        action: str,
        point_number: Optional[int],
        old_value: Optional[str],
        new_value: Optional[str],
    ) -> None: ...

    def get_history(self, project_id: int) -> list[HistoryEntry]: ...

