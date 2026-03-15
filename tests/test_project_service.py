# tests/test_project_service.py

from __future__ import annotations

from app.services.history_service import HistoryService
from app.services.project_service import ProjectService


def test_list_projects_empty(project_repo, history_repo):
    svc = ProjectService(project_repo, HistoryService(history_repo))
    assert svc.list_projects() == []


def test_add_project(project_repo, history_repo):
    svc = ProjectService(project_repo, HistoryService(history_repo))
    p = svc.add_project("P1", "a.dxf", "desc")
    assert p.project_id >= 1
    assert p.name == "P1"
    assert p.dxf_file == "a.dxf"
    assert p.description == "desc"
    all_p = svc.list_projects()
    assert len(all_p) == 1
    assert all_p[0].name == "P1"


def test_delete_project(project_repo, history_repo):
    svc = ProjectService(project_repo, HistoryService(history_repo))
    p = svc.add_project("P1", "a.dxf", "")
    svc.delete_project(p.project_id)
    assert svc.list_projects() == []


def test_add_point(project_repo, history_repo):
    svc = ProjectService(project_repo, HistoryService(history_repo))
    p = svc.add_project("P1", "a.dxf", "")
    pt = svc.add_point(
        p.project_id, 1, "D1", "Диаметр",
        "25.0", "+0.02", "-0.01", 10.0, 20.0, "",
    )
    assert pt is not None
    assert pt.number == 1
    loaded = project_repo.get_by_id(p.project_id)
    assert loaded is not None
    assert len(loaded.points) == 1
    assert loaded.points[0].name == "D1"


def test_update_point(project_repo, history_repo):
    svc = ProjectService(project_repo, HistoryService(history_repo))
    p = svc.add_project("P1", "a.dxf", "")
    svc.add_point(
        p.project_id, 1, "D1", "Диаметр",
        "25.0", "+0.02", "-0.01", 0, 0, "",
    )
    svc.update_point(
        p.project_id, 1, "D1 new", "Диаметр",
        "25.0", "+0.02", "-0.01", 0, 0, "",
        measured_value="25.015",
    )
    loaded = project_repo.get_by_id(p.project_id)
    assert loaded.points[0].name == "D1 new"
    assert loaded.points[0].measured_value == "25.015"


def test_remove_point(project_repo, history_repo):
    svc = ProjectService(project_repo, HistoryService(history_repo))
    p = svc.add_project("P1", "a.dxf", "")
    svc.add_point(
        p.project_id, 1, "D1", "Диаметр",
        "25.0", "0", "0", 0, 0, "",
    )
    svc.remove_point(p.project_id, 1)
    loaded = project_repo.get_by_id(p.project_id)
    assert len(loaded.points) == 0


def test_get_history(project_repo, history_repo):
    svc = ProjectService(project_repo, HistoryService(history_repo))
    p = svc.add_project("P1", "a.dxf", "")
    svc.add_point(
        p.project_id, 1, "D1", "Диаметр",
        "25.0", "0", "0", 0, 0, "",
    )
    hist = svc.get_history(p.project_id)
    assert len(hist) >= 1
    assert hist[0].action == "add_point"
