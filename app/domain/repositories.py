from __future__ import annotations

from typing import Protocol

from app.domain.models import Project


class IProjectRepository(Protocol):
    """Интерфейс репозитория проектов."""

    def list_all(self) -> list[Project]: ...

    def get_by_id(self, project_id: int) -> Project | None: ...

    def add(self, project: Project) -> None: ...

    def remove(self, project_id: int) -> None: ...

    def next_id(self) -> int: ...
