from __future__ import annotations

import logging
from collections.abc import Callable

from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.domain.models import Project
from app.services.project_service import ProjectService
from app.ui.components.project_dialog import ProjectDialog
from app.ui.components.stat_card import StatCard
from app.ui.pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ProjectsPage(BasePage):
    def __init__(
        self,
        service: ProjectService,
        on_open_project: Callable[[Project], None],
    ) -> None:
        super().__init__(
            "Панель ОТК",
            "Добавляйте проекты, удаляйте их"
            " и открывайте для работы",
        )
        self._service = service
        self._on_open_project = on_open_project

        self._build()
        self.refresh()

    def _build(self) -> None:
        btns = QHBoxLayout()
        btns.addStretch()
        add_btn = QPushButton("Добавить проект")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self._add_project)

        del_btn = QPushButton("Удалить проект")
        del_btn.setObjectName("dangerButton")
        del_btn.clicked.connect(self._delete_project)

        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        self._root.addLayout(btns)

        stats = QGridLayout()
        stats.addWidget(
            StatCard("Проектов", "0", "активных в системе"),
            0, 0,
        )
        stats.addWidget(
            StatCard("Точек", "0", "контрольных размеров"),
            0, 1,
        )
        stats.addWidget(
            StatCard("DXF", "1", "демо-чертеж в комплекте"),
            0, 2,
        )
        stats.addWidget(
            StatCard("Статус", "MVP", "готов к тесту"),
            0, 3,
        )
        self._root.addLayout(stats)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)

        self._table = QTableWidget(0, 5)
        self._table.setAlternatingRowColors(True)
        self._table.setHorizontalHeaderLabels([
            "ID", "Проект", "DXF", "Описание",
            "Последний контроль",
        ])
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch,
        )
        self._table.verticalHeader().setVisible(False)
        self._table.cellDoubleClicked.connect(
            self._on_double_click,
        )
        card_layout.addWidget(self._table)

        open_btn = QPushButton("Открыть выбранный проект")
        open_btn.clicked.connect(self._open_current)
        card_layout.addWidget(open_btn)
        self._root.addWidget(card, 1)

    def refresh(self) -> None:
        projects = self._service.list_projects()
        self._table.setRowCount(len(projects))
        total_points = 0
        for row, project in enumerate(projects):
            total_points += len(project.points)
            vals = [
                str(project.project_id),
                project.name,
                project.dxf_file,
                project.description,
                project.last_control,
            ]
            for col, val in enumerate(vals):
                self._table.setItem(
                    row, col, QTableWidgetItem(val),
                )
        if projects:
            self._table.selectRow(0)
        stat_cards = self.findChildren(StatCard)
        if len(stat_cards) >= 2:
            stat_cards[0].findChildren(QLabel)[1].setText(
                str(len(projects)),
            )
            stat_cards[1].findChildren(QLabel)[1].setText(
                str(total_points),
            )

    def _selected_project(self) -> Project | None:
        row = self._table.currentRow()
        projects = self._service.list_projects()
        if row < 0 or row >= len(projects):
            return None
        return projects[row]

    def _add_project(self) -> None:
        logger.debug("Действие: добавить проект")
        dlg = ProjectDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name, dxf, desc = dlg.data()
        if not name:
            QMessageBox.warning(
                self, "Ошибка",
                "Введите название проекта",
            )
            return
        self._service.add_project(name, dxf, desc)
        self.refresh()

    def _delete_project(self) -> None:
        logger.debug("Действие: удалить проект")
        project = self._selected_project()
        if not project:
            QMessageBox.warning(
                self, "Нет выбора", "Выберите проект",
            )
            return
        ans = QMessageBox.question(
            self, "Удаление",
            f"Удалить проект '{project.name}'?",
        )
        if ans != QMessageBox.StandardButton.Yes:
            return
        self._service.delete_project(project.project_id)
        self.refresh()

    def _open_current(self) -> None:
        project = self._selected_project()
        if project:
            logger.info(
                "Открытие проекта: %s", project.name,
            )
            self._on_open_project(project)

    def _on_double_click(
        self, row: int, col: int,
    ) -> None:
        self._open_current()
