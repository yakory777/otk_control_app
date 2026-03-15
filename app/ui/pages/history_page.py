# app/ui/pages/history_page.py

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.services.project_service import ProjectService
from app.ui.pages.base_page import BasePage


class HistoryPage(BasePage):
    """Страница истории изменений по проектам."""

    def __init__(self, service: ProjectService) -> None:
        super().__init__(
            "История изменений",
            "Журнал изменений размеров и действий",
        )
        self._service = service

        col = QVBoxLayout()
        filter_row = QFrame()
        filter_lay = QVBoxLayout(filter_row)
        filter_lay.addWidget(QLabel("Проект:"))
        self._project_combo = QComboBox()
        self._project_combo.setMinimumWidth(280)
        self._project_combo.currentIndexChanged.connect(
            self._on_project_changed,
        )
        filter_lay.addWidget(self._project_combo)
        col.addWidget(filter_row)

        self._table = QTableWidget(0, 5)
        self._table.setAlternatingRowColors(True)
        self._table.setHorizontalHeaderLabels([
            "Дата", "Оператор", "Действие",
            "Старое", "Новое",
        ])
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch,
        )
        self._table.verticalHeader().setVisible(False)
        col.addWidget(self._table, 1)

        self._root.addLayout(col, 1)

    def refresh(self) -> None:
        """Обновить список проектов и таблицу истории."""
        projects = self._service.list_projects()
        self._project_combo.clear()
        self._project_combo.addItem("— Выберите проект —", None)
        for p in projects:
            self._project_combo.addItem(
                f"{p.name} (id={p.project_id})",
                p.project_id,
            )
        self._fill_history()

    def _on_project_changed(self) -> None:
        self._fill_history()

    def _fill_history(self) -> None:
        project_id = self._project_combo.currentData()
        if project_id is None:
            self._table.setRowCount(0)
            return
        entries = self._service.get_history(project_id)
        self._table.setRowCount(len(entries))
        for row, e in enumerate(entries):
            self._table.setItem(
                row, 0,
                QTableWidgetItem(e.timestamp),
            )
            self._table.setItem(
                row, 1,
                QTableWidgetItem(e.operator or "—"),
            )
            action = e.action or "—"
            point = f" №{e.point_number}" if e.point_number is not None else ""
            self._table.setItem(
                row, 2,
                QTableWidgetItem(f"{action}{point}"),
            )
            self._table.setItem(
                row, 3,
                QTableWidgetItem(e.old_value or "—"),
            )
            self._table.setItem(
                row, 4,
                QTableWidgetItem(e.new_value or "—"),
            )
