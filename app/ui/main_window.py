# app/ui/main_window.py

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from app.domain.models import Project
from app.infrastructure.sqlite_repository import (
    SqliteHistoryRepository,
    SqliteProjectRepository,
)
from app.services.config_service import ConfigService
from app.services.export_service import ExportService
from app.services.history_service import HistoryService
from app.services.project_service import ProjectService
from app.ui.components.sidebar import Sidebar
from app.ui.pages.analytics_page import AnalyticsPage
from app.ui.pages.history_page import HistoryPage
from app.ui.pages.measurements_page import MeasurementsPage
from app.ui.pages.projects_page import ProjectsPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.pages.template_page import TemplatePage
from app.ui.style import STYLE

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        logger.info("Инициализация MainWindow")

        db_path = "data/otk.db"
        project_repo = SqliteProjectRepository(db_path)
        history_repo = SqliteHistoryRepository(db_path)
        history_service = HistoryService(history_repo)
        self._service = ProjectService(
            project_repo,
            history_service,
        )

        self.setWindowTitle("OTK DXF Inspector")
        self.resize(1680, 960)

        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._pages = QStackedWidget()
        config_svc = ConfigService()
        config = config_svc.load()
        export_svc = ExportService(operator=config.operator)
        self._projects_page = ProjectsPage(
            self._service, self._open_project,
        )
        self._template_page = TemplatePage(self._service)
        self._measurements_page = MeasurementsPage(
            self._service,
            export_svc,
        )
        self._analytics_page = AnalyticsPage(
            self._service,
            export_svc,
        )
        self._history_page = HistoryPage(self._service)
        self._settings_page = SettingsPage(config_svc)

        for page in [
            self._projects_page,
            self._template_page,
            self._measurements_page,
            self._analytics_page,
            self._history_page,
            self._settings_page,
        ]:
            self._pages.addWidget(page)

        self._sidebar = Sidebar(self._switch_page)
        root.addWidget(self._sidebar)
        root.addWidget(self._pages, 1)
        self.setCentralWidget(central)
        self.setStyleSheet(STYLE)

    def _switch_page(self, index: int) -> None:
        logger.debug("Переключение на страницу %d", index)
        if index == 1:
            self._template_page.refresh()
        elif index == 2:
            self._measurements_page.refresh()
        elif index == 3:
            self._analytics_page.refresh()
        elif index == 4:
            self._history_page.refresh()
        self._pages.setCurrentIndex(index)

    def _open_project(self, project: Project) -> None:
        logger.info(
            "Открытие проекта: id=%d, name=%s",
            project.project_id, project.name,
        )
        self._service.current_project_id = project.project_id
        self._template_page.refresh()
        self._sidebar.menu.setCurrentRow(1)
        self._pages.setCurrentWidget(self._template_page)


def run_app() -> None:
    logger.info("Запуск OTK DXF Inspector")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    logger.info("Окно показано, вход в event loop")
    sys.exit(app.exec())
