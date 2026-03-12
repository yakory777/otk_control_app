from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.project_service import ProjectService
from app.ui.components.dxf_view import DxfView


class TemplatePage(QWidget):
    def __init__(self, service: ProjectService) -> None:
        super().__init__()
        self._service = service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        head = QHBoxLayout()
        left = QVBoxLayout()
        self._title = QLabel("Шаблон контроля")
        self._title.setObjectName("pageTitle")
        self._sub = QLabel(
            "DXF viewer, контрольные точки и свойства проекта",
        )
        self._sub.setObjectName("pageSub")
        left.addWidget(self._title)
        left.addWidget(self._sub)
        head.addLayout(left)
        head.addStretch()
        head.addWidget(QPushButton("Добавить размер"))
        head.addWidget(QPushButton("Удалить размер"))
        layout.addLayout(head)

        splitter = QHBoxLayout()

        left_card = QGroupBox("Проект")
        left_layout = QVBoxLayout(left_card)
        self._info = QLabel("")
        self._info.setWordWrap(True)
        left_layout.addWidget(self._info)
        left_layout.addStretch()

        center = QGroupBox("DXF Viewer")
        center_layout = QVBoxLayout(center)
        self._dxf_view = DxfView()
        center_layout.addWidget(self._dxf_view)

        right = QGroupBox("Контрольные точки")
        right_layout = QVBoxLayout(right)
        self._table = QTableWidget(0, 6)
        self._table.setAlternatingRowColors(True)
        self._table.setHorizontalHeaderLabels([
            "№", "Название", "Тип", "Истинное", "+", "-",
        ])
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch,
        )
        self._table.verticalHeader().setVisible(False)
        right_layout.addWidget(self._table)

        splitter.addWidget(left_card, 1)
        splitter.addWidget(center, 2)
        splitter.addWidget(right, 2)
        layout.addLayout(splitter, 1)
        self.refresh()

    def refresh(self) -> None:
        project = self._service.current_project()
        if not project:
            self._info.setText("Нет выбранного проекта")
            self._table.setRowCount(0)
            return
        self._info.setText(
            f"Проект: {project.name}\n"
            f"DXF: {project.dxf_file}\n"
            f"Описание: {project.description}\n"
            f"Последний контроль: {project.last_control}"
        )
        if project.dxf_file:
            self._dxf_view.load_file(project.dxf_file)
        self._table.setRowCount(len(project.points))
        for row, pt in enumerate(project.points):
            vals = [
                str(pt.number), pt.name, pt.kind,
                pt.true_value, pt.tol_plus, pt.tol_minus,
            ]
            for col, val in enumerate(vals):
                self._table.setItem(
                    row, col, QTableWidgetItem(val),
                )
