from __future__ import annotations

from app.domain.models import ControlPoint, Project
from app.domain.repositories import IProjectRepository


class ProjectService:
    """Use cases для работы с проектами."""

    def __init__(self, repo: IProjectRepository) -> None:
        self._repo = repo
        self._current_project_id: int | None = 1

    def list_projects(self) -> list[Project]:
        return self._repo.list_all()

    @property
    def current_project_id(self) -> int | None:
        return self._current_project_id

    @current_project_id.setter
    def current_project_id(self, value: int | None) -> None:
        self._current_project_id = value

    def current_project(self) -> Project | None:
        if self._current_project_id is not None:
            project = self._repo.get_by_id(
                self._current_project_id,
            )
            if project is not None:
                return project
        projects = self._repo.list_all()
        return projects[0] if projects else None

    def add_project(
        self,
        name: str,
        dxf_file: str,
        description: str,
    ) -> Project:
        project = Project(
            project_id=self._repo.next_id(),
            name=name,
            dxf_file=dxf_file,
            description=description,
            last_control="\u2014",
        )
        self._repo.add(project)
        self._current_project_id = project.project_id
        return project

    def delete_project(self, project_id: int) -> None:
        self._repo.remove(project_id)
        if self._current_project_id == project_id:
            projects = self._repo.list_all()
            self._current_project_id = (
                projects[0].project_id if projects else None
            )

    def add_point(
        self,
        name: str,
        kind: str,
        true_value: str,
        tol_plus: str,
        tol_minus: str,
    ) -> ControlPoint | None:
        """Добавить контрольный размер в текущий проект."""
        project = self.current_project()
        if project is None:
            return None
        number = (
            max((p.number for p in project.points), default=0) + 1
        )
        point = ControlPoint(
            number=number,
            name=name,
            kind=kind,
            true_value=true_value,
            tol_plus=tol_plus,
            tol_minus=tol_minus,
        )
        project.points.append(point)
        return point

    def remove_point(self, number: int) -> None:
        """Удалить контрольный размер по номеру из текущего проекта."""
        project = self.current_project()
        if project is None:
            return
        project.points = [
            p for p in project.points if p.number != number
        ]
