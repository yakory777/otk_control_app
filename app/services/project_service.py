# app/services/project_service.py

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import cast

from app.domain.dxf_entities import DxfEntityInfo
from app.domain.models import ControlPoint, HistoryEntry, Project

logger = logging.getLogger(__name__)


class ProjectService:
    """Сервис проектов и контрольных точек."""

    def __init__(
        self,
        project_repo,
        history_service=None,
    ) -> None:
        self._project_repo = project_repo
        self._history_service = history_service
        self._current_project_id: int | None = None

    @property
    def current_project_id(self) -> int | None:
        return self._current_project_id

    @current_project_id.setter
    def current_project_id(self, value: int | None) -> None:
        self._current_project_id = value

    def current_project(self) -> Project | None:
        if self._current_project_id is None:
            return None
        return cast(
            Project | None,
            self._project_repo.get_by_id(self._current_project_id),
        )

    def list_projects(self) -> list[Project]:
        return cast(list[Project], self._project_repo.list_all())

    def add_project(
        self,
        name: str,
        dxf_file: str,
        description: str = "",
    ) -> Project:
        next_id = self._project_repo.next_id()
        project = Project(
            project_id=next_id,
            name=name,
            dxf_file=dxf_file,
            description=description,
            last_control="",
            points=[],
        )
        self._project_repo.add(project)
        logger.info("Добавлен проект: id=%d, name=%s", next_id, name)
        return project

    def delete_project(self, project_id: int) -> None:
        self._project_repo.remove(project_id)
        if self._current_project_id == project_id:
            self._current_project_id = None
        logger.info("Удалён проект id=%d", project_id)

    def update_last_control(self, project_id: int, value: str) -> None:
        """Обновить дату последнего контроля по проекту."""
        project = self._project_repo.get_by_id(project_id)
        if project:
            project.last_control = value
            self._project_repo.update(project)

    def add_point(
        self,
        project_id: int,
        number: int,
        name: str,
        kind: str,
        true_value: str,
        tol_plus: str = "0",
        tol_minus: str = "0",
        x: float = 0,
        y: float = 0,
        entity_handle: str = "",
    ) -> ControlPoint | None:
        project = self._project_repo.get_by_id(project_id)
        if not project:
            return None
        point = ControlPoint(
            number=number,
            name=name,
            kind=kind,
            true_value=true_value,
            tol_plus=tol_plus,
            tol_minus=tol_minus,
            x=x,
            y=y,
            entity_handle=entity_handle,
            measured_value="",
        )
        project.points.append(point)
        self._project_repo.update(project)
        if self._history_service:
            self._history_service.log(
                project_id, "", "add_point", number, None, name,
            )
        return point

    def update_point(
        self,
        project_id: int,
        number: int,
        name: str,
        kind: str,
        true_value: str,
        tol_plus: str = "0",
        tol_minus: str = "0",
        x: float = 0,
        y: float = 0,
        entity_handle: str = "",
        measured_value: str | None = None,
    ) -> None:
        project = self._project_repo.get_by_id(project_id)
        if not project:
            return
        for pt in project.points:
            if pt.number == number:
                old_val = pt.measured_value or ""
                pt.name = name
                pt.kind = kind
                pt.true_value = true_value
                pt.tol_plus = tol_plus
                pt.tol_minus = tol_minus
                pt.x = x
                pt.y = y
                pt.entity_handle = entity_handle
                if measured_value is not None:
                    pt.measured_value = measured_value
                self._project_repo.update(project)
                if self._history_service:
                    self._history_service.log(
                        project_id, "", "update_point",
                        number, old_val, pt.measured_value or "",
                    )
                return
        logger.warning(
            "Точка №%d не найдена в проекте %d",
            number, project_id,
        )

    def remove_point(self, project_id: int, number: int) -> None:
        project = self._project_repo.get_by_id(project_id)
        if not project:
            return
        removed = [p for p in project.points if p.number == number]
        project.points = [p for p in project.points if p.number != number]
        self._project_repo.update(project)
        if self._history_service and removed:
            self._history_service.log(
                project_id, "", "remove_point",
                number, removed[0].name, "",
            )
        logger.debug("Удалена точка №%d из проекта %d", number, project_id)

    def auto_import_dimensions(
        self,
        project_id: int,
        entities: Sequence[DxfEntityInfo],
    ) -> int:
        project = self._project_repo.get_by_id(project_id)
        if not project:
            return 0
        start = max((p.number for p in project.points), default=0) + 1
        for i, dim in enumerate(entities):
            pt = ControlPoint(
                number=start + i,
                name=dim.label or f"Размер {start + i}",
                kind=dim.kind or "Линейный",
                true_value=str(dim.value) if dim.value is not None else "0",
                tol_plus="0",
                tol_minus="0",
                x=dim.center_x or 0,
                y=dim.center_y or 0,
                entity_handle=str(dim.handle) if dim.handle else "",
                measured_value="",
            )
            project.points.append(pt)
        self._project_repo.update(project)
        logger.info(
            "Импортировано %d размеров в проект %d",
            len(entities), project_id,
        )
        return len(entities)

    def get_history(self, project_id: int) -> list[HistoryEntry]:
        if not self._history_service:
            return []
        return cast(
            list[HistoryEntry],
            self._history_service.get_history(project_id),
        )
