from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from app.services.project_service import ProjectService
from app.domain.models import Project
from app.infrastructure.repositories import (
    InMemoryProjectRepository,
)
from app.ui.components.sidebar import Sidebar
from app.ui.pages.analytics_page import AnalyticsPage
from app.ui.pages.history_page import HistoryPage
from app.ui.pages.measurements_page import MeasurementsPage
from app.ui.pages.projects_page import ProjectsPage
from app.ui.pages.reports_page import ReportsPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.pages.template_page import TemplatePage
from app.ui.style import STYLE


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        repo = InMemoryProjectRepository()
        self._service = ProjectService(repo)

        self.setWindowTitle("OTK DXF Inspector")
        self.resize(1680, 960)

        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._sidebar = Sidebar(self._switch_page)
        root.addWidget(self._sidebar)

        self._pages = QStackedWidget()
        self._projects_page = ProjectsPage(
            self._service, self._open_project,
        )
        self._template_page = TemplatePage(self._service)
        self._measurements_page = MeasurementsPage(
            self._service,
        )
        self._analytics_page = AnalyticsPage()
        self._reports_page = ReportsPage()
        self._history_page = HistoryPage()
        self._settings_page = SettingsPage()

        for page in [
            self._projects_page,
            self._template_page,
            self._measurements_page,
            self._analytics_page,
            self._reports_page,
            self._history_page,
            self._settings_page,
        ]:
            self._pages.addWidget(page)

        root.addWidget(self._pages, 1)
        self.setCentralWidget(central)
        self.setStyleSheet(STYLE)

    def _switch_page(self, index: int) -> None:
        if index == 1:
            self._template_page.refresh()
        self._pages.setCurrentIndex(index)

    def _open_project(self, project: Project) -> None:
        self._service.current_project_id = project.project_id
        self._template_page.refresh()
        self._sidebar.menu.setCurrentRow(1)
        self._pages.setCurrentWidget(self._template_page)


def run_app() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
