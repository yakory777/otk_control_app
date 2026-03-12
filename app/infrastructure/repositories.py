from __future__ import annotations

from app.domain.models import ControlPoint, Project


class InMemoryProjectRepository:
    """In-memory реализация репозитория проектов."""

    def __init__(self) -> None:
        self._projects: list[Project] = self._seed()

    def list_all(self) -> list[Project]:
        return list(self._projects)

    def get_by_id(self, project_id: int) -> Project | None:
        for project in self._projects:
            if project.project_id == project_id:
                return project
        return None

    def add(self, project: Project) -> None:
        self._projects.insert(0, project)

    def remove(self, project_id: int) -> None:
        self._projects = [
            p for p in self._projects
            if p.project_id != project_id
        ]

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
                        "248.000", "205.000",
                    ),
                    ControlPoint(
                        2, "Длина L2", "Линейный",
                        "84.500", "+0.050", "-0.050",
                        "520.000", "205.000",
                    ),
                    ControlPoint(
                        3, "Отверстие H3", "Диаметр",
                        "8.200", "+0.015", "-0.015",
                        "610.000", "135.000",
                    ),
                    ControlPoint(
                        4, "Радиус R4", "Радиус",
                        "3.000", "+0.010", "-0.010",
                        "430.000", "300.000",
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
