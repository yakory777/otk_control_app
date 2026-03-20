from __future__ import annotations

import logging

from app.domain.models import ControlPoint, Project

logger = logging.getLogger(__name__)


class InMemoryProjectRepository:
    """In-memory реализация репозитория проектов."""

    def __init__(self) -> None:
        self._projects: list[Project] = self._seed()
        logger.info(
            "Репозиторий инициализирован: %d проектов",
            len(self._projects),
        )

    def list_all(self) -> list[Project]:
        return list(self._projects)

    def get_by_id(self, project_id: int) -> Project | None:
        for project in self._projects:
            if project.project_id == project_id:
                return project
        return None

    def add(self, project: Project) -> None:
        self._projects.insert(0, project)
        logger.debug(
            "Проект сохранён: id=%d, name=%s",
            project.project_id, project.name,
        )

    def remove(self, project_id: int) -> None:
        before = len(self._projects)
        self._projects = [
            p for p in self._projects
            if p.project_id != project_id
        ]
        logger.debug(
            "Удалён проект id=%d (было %d, стало %d)",
            project_id, before, len(self._projects),
        )

    def next_id(self) -> int:
        return max(
            (p.project_id for p in self._projects),
            default=0,
        ) + 1

    @staticmethod
    def _seed() -> list[Project]:
        """Демо-данные для первого запуска."""
        return [
            Project(
                project_id=1,
                name="Корпус 12А",
                dxf_file="data/examples/dra2 2.dxf",
                description="Демо-проект для ОТК",
                last_control="12.03.2026",
                points=[
                    ControlPoint(
                        1, "Диаметр D1", "Диаметр",
                        "25.000", "+0.020", "-0.010",
                        248.0, 205.0,
                        measured_value="25.012",
                    ),
                    ControlPoint(
                        2, "Длина L2", "Линейный",
                        "84.500", "+0.050", "-0.050",
                        520.0, 205.0,
                        measured_value="84.471",
                    ),
                    ControlPoint(
                        3, "Отверстие H3", "Диаметр",
                        "8.200", "+0.015", "-0.015",
                        610.0, 135.0,
                        measured_value="8.214",
                    ),
                    ControlPoint(
                        4, "Радиус R4", "Радиус",
                        "3.000", "+0.010", "-0.010",
                        430.0, 300.0,
                        measured_value="3.019",
                    ),
                ],
            ),
            Project(
                project_id=2,
                name="Втулка B7",
                dxf_file="data/examples/dra2 3.dxf",
                description="Вспомогательный проект",
                last_control="10.03.2026",
            ),
        ]
