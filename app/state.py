from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ControlPoint:
    number: int
    name: str
    kind: str
    true_value: str
    tol_plus: str
    tol_minus: str
    x: str = "0.000"
    y: str = "0.000"


@dataclass
class Project:
    project_id: int
    name: str
    dxf_file: str
    description: str
    last_control: str
    points: List[ControlPoint] = field(default_factory=list)


class AppState:
    def __init__(self) -> None:
        self.projects: List[Project] = [
            Project(
                1,
                "Корпус 12А",
                "demo_part.dxf",
                "Демо-проект для ОТК",
                "12.03.2026",
                [
                    ControlPoint(1, "Диаметр D1", "Диаметр", "25.000", "+0.020", "-0.010", "248.000", "205.000"),
                    ControlPoint(2, "Длина L2", "Линейный", "84.500", "+0.050", "-0.050", "520.000", "205.000"),
                    ControlPoint(3, "Отверстие H3", "Диаметр", "8.200", "+0.015", "-0.015", "610.000", "135.000"),
                    ControlPoint(4, "Радиус R4", "Радиус", "3.000", "+0.010", "-0.010", "430.000", "300.000"),
                ],
            ),
            Project(2, "Втулка B7", "demo_part.dxf", "Вспомогательный проект", "10.03.2026", []),
        ]
        self.current_project_id: int | None = 1

    def current_project(self) -> Project | None:
        for project in self.projects:
            if project.project_id == self.current_project_id:
                return project
        return self.projects[0] if self.projects else None

    def add_project(self, name: str, dxf_file: str, description: str) -> Project:
        next_id = max((p.project_id for p in self.projects), default=0) + 1
        project = Project(next_id, name, dxf_file, description, "—", [])
        self.projects.insert(0, project)
        self.current_project_id = project.project_id
        return project

    def delete_project(self, project_id: int) -> None:
        self.projects = [p for p in self.projects if p.project_id != project_id]
        if self.current_project_id == project_id:
            self.current_project_id = self.projects[0].project_id if self.projects else None
