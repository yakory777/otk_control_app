# app/infrastructure/sqlite_repository.py

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, cast

from app.domain.models import ControlPoint, HistoryEntry, Project
from app.infrastructure.database import Database

logger = logging.getLogger(__name__)


def _point_from_row(row: tuple) -> ControlPoint:
    (
        _pk, _project_id, number, name, kind,
        true_value, tol_plus, tol_minus, x, y,
        entity_handle, measured_value,
    ) = row
    return ControlPoint(
        number=int(number),
        name=name or "",
        kind=kind or "",
        true_value=str(true_value) if true_value is not None else "",
        tol_plus=str(tol_plus) if tol_plus is not None else "0",
        tol_minus=str(tol_minus) if tol_minus is not None else "0",
        x=float(x or 0),
        y=float(y or 0),
        entity_handle=entity_handle or "",
        measured_value=(
            str(measured_value) if measured_value is not None else ""
        ),
    )


def _history_from_row(row: tuple) -> HistoryEntry:
    return HistoryEntry(
        entry_id=row[0],
        project_id=row[1],
        timestamp=row[2],
        operator=row[3] or "",
        action=row[4] or "",
        point_number=row[5],
        old_value=row[6] or "",
        new_value=row[7] or "",
    )


class SqliteProjectRepository:
    """Репозиторий проектов на SQLite."""

    def __init__(self, db_path: str) -> None:
        self._db = Database(db_path)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        Database.init_db(self._db.get_connection())

    def _conn(self):
        return self._db.get_connection()

    def list_all(self) -> list[Project]:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, dxf_file, description, last_control "
            "FROM projects",
        )
        projects = []
        for row in cur.fetchall():
            pid, name, dxf_file, description, last_control = row
            points = self._load_points(conn, pid)
            projects.append(
                Project(
                    project_id=pid,
                    name=name or "",
                    dxf_file=dxf_file or "",
                    description=description or "",
                    last_control=last_control or "",
                    points=points,
                ),
            )
        return projects

    def _load_points(self, conn, project_id: int) -> list[ControlPoint]:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, project_id, number, name, kind, true_value, "
            "tol_plus, tol_minus, x, y, entity_handle, measured_value "
            "FROM control_points WHERE project_id = ? ORDER BY number",
            (project_id,),
        )
        return [_point_from_row(r) for r in cur.fetchall()]

    def get_by_id(self, project_id: int) -> Optional[Project]:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, dxf_file, description, last_control "
            "FROM projects WHERE id = ?",
            (project_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        pid, name, dxf_file, description, last_control = row
        points = self._load_points(conn, pid)
        return Project(
            project_id=pid,
            name=name or "",
            dxf_file=dxf_file or "",
            description=description or "",
            last_control=last_control or "",
            points=points,
        )

    def add(self, project: Project) -> None:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO projects "
            "(id, name, dxf_file, description, last_control) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                project.project_id,
                project.name,
                project.dxf_file,
                project.description,
                project.last_control or "",
            ),
        )
        for pt in project.points:
            self._insert_point(cur, project.project_id, pt)
        conn.commit()
        logger.debug(
            "Проект сохранён: id=%d, name=%s",
            project.project_id, project.name,
        )

    def _insert_point(self, cur, project_id: int, pt: ControlPoint) -> None:
        try:
            tv = float(pt.true_value) if pt.true_value else 0.0
        except (ValueError, TypeError):
            tv = 0.0
        try:
            tp = float(pt.tol_plus)
        except (ValueError, TypeError):
            tp = 0.0
        try:
            tm = float(pt.tol_minus)
        except (ValueError, TypeError):
            tm = 0.0
        mv = float(pt.measured_value) if pt.measured_value else None
        cur.execute(
            "INSERT INTO control_points "
            "(project_id, number, name, kind, true_value, tol_plus, tol_minus,"
            " x, y, entity_handle, measured_value) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                project_id, pt.number, pt.name, pt.kind, tv, tp, tm,
                pt.x, pt.y, pt.entity_handle, mv,
            ),
        )

    def update(self, project: Project) -> None:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE projects SET name = ?, dxf_file = ?, description = ?, "
            "last_control = ? WHERE id = ?",
            (
                project.name,
                project.dxf_file,
                project.description,
                project.last_control or "",
                project.project_id,
            ),
        )
        cur.execute(
            "DELETE FROM control_points WHERE project_id = ?",
            (project.project_id,),
        )
        for pt in project.points:
            self._insert_point(cur, project.project_id, pt)
        conn.commit()
        logger.debug("Проект обновлён: id=%d", project.project_id)

    def remove(self, project_id: int) -> None:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM control_points WHERE project_id = ?",
            (project_id,),
        )
        cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        logger.debug("Удалён проект id=%d", project_id)

    def next_id(self) -> int:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT IFNULL(MAX(id), 0) + 1 FROM projects")
        row = cur.fetchone()
        return cast(int, row[0] if row is not None else 1)


class SqliteHistoryRepository:
    """Репозиторий истории изменений на SQLite."""

    def __init__(self, db_path: str) -> None:
        self._db = Database(db_path)
        Database.init_db(self._db.get_connection())

    def _conn(self):
        return self._db.get_connection()

    def log(
        self,
        project_id: int,
        operator: str,
        action: str,
        point_number: Optional[int],
        old_value: Optional[str],
        new_value: Optional[str],
    ) -> None:
        conn = self._conn()
        cur = conn.cursor()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            "INSERT INTO history "
            "(project_id, timestamp, operator, action, point_number, "
            "old_value, new_value) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                project_id, ts, operator or "", action,
                point_number, old_value or "", new_value or "",
            ),
        )
        conn.commit()

    def get_history(self, project_id: int) -> list[HistoryEntry]:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, project_id, timestamp, operator, action, "
            "point_number, old_value, new_value FROM history "
            "WHERE project_id = ? ORDER BY id DESC",
            (project_id,),
        )
        return [_history_from_row(r) for r in cur.fetchall()]
