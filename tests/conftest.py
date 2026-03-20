# tests/conftest.py

from __future__ import annotations

import pytest

from app.domain.models import ControlPoint, Project
from app.infrastructure.sqlite_repository import (
    SqliteHistoryRepository,
    SqliteProjectRepository,
)
from app.services.history_service import HistoryService
from app.services.project_service import ProjectService


@pytest.fixture
def db_path():
    """In-memory SQLite для тестов."""
    return ":memory:"


@pytest.fixture
def project_repo(db_path):
    return SqliteProjectRepository(db_path)


@pytest.fixture
def history_repo(db_path):
    return SqliteHistoryRepository(db_path)


@pytest.fixture
def history_service(history_repo):
    return HistoryService(history_repo)


@pytest.fixture
def project_service(project_repo, history_service):
    return ProjectService(project_repo, history_service)


@pytest.fixture
def sample_project():
    """Проект с двумя точками."""
    return Project(
        project_id=1,
        name="Тест",
        dxf_file="test.dxf",
        description="",
        last_control="",
        points=[
            ControlPoint(
                1, "D1", "Диаметр",
                "25.0", "+0.02", "-0.01",
                0, 0, "", "25.01",
            ),
            ControlPoint(
                2, "L2", "Линейный",
                "84.5", "+0.05", "-0.05",
                0, 0, "", "",
            ),
        ],
    )
