from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.project_service import ProjectService
from PySide6.QtWidgets import QDialog

from app.ui.components.dxf_view import DxfView
from app.ui.components.point_dialog import PointDialog


class TemplatePage(QWidget):
    def __init__(self, service: ProjectService) -> None:
        super().__init__()
        self._service = service
        self._loaded_dxf: str | None = None

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

        self._add_btn = QPushButton("Добавить размер")
        self._del_btn = QPushButton("Удалить размер")
        self._add_btn.clicked.connect(self._add_point)
        self._del_btn.clicked.connect(self._delete_point)
        head.addWidget(self._add_btn)
        head.addWidget(self._del_btn)
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
            "№", "Название", "Тип", "Истинное", "+", "−",
        ])
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch,
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows,
        )
        right_layout.addWidget(self._table)

        splitter.addWidget(left_card, 1)
        splitter.addWidget(center, 2)
        splitter.addWidget(right, 2)
        layout.addLayout(splitter, 1)
        self.refresh()

    def refresh(self) -> None:
        """Обновить страницу при смене текущего проекта."""
        project = self._service.current_project()
        if not project:
            self._info.setText("Нет выбранного проекта")
            self._table.setRowCount(0)
            self._loaded_dxf = None
            return

        self._info.setText(
            f"Проект: {project.name}\n"
            f"DXF: {project.dxf_file}\n"
            f"Описание: {project.description}\n"
            f"Последний контроль: {project.last_control}"
        )

        if project.dxf_file and project.dxf_file != self._loaded_dxf:
            self._dxf_view.load_file(project.dxf_file)
            self._loaded_dxf = project.dxf_file

        self._refresh_table()

    def _refresh_table(self) -> None:
        """Перерисовать только таблицу контрольных точек."""
        project = self._service.current_project()
        if not project:
            self._table.setRowCount(0)
            return
        self._table.setRowCount(len(project.points))
        for row, pt in enumerate(project.points):
            vals = [
                str(pt.number), pt.name, pt.kind,
                pt.true_value, pt.tol_plus, pt.tol_minus,
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                self._table.setItem(row, col, item)

    def _add_point(self) -> None:
        if self._service.current_project() is None:
            QMessageBox.warning(
                self, "Нет проекта", "Сначала выберите проект.",
            )
            return
        dlg = PointDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name, kind, true_val, tol_plus, tol_minus = dlg.data()
        if not name:
            QMessageBox.warning(
                self, "Пустое название",
                "Укажите название размера.",
            )
            return
        self._service.add_point(name, kind, true_val, tol_plus, tol_minus)
        self._refresh_table()

    def _delete_point(self) -> None:
        selected = self._table.selectedItems()
        if not selected:
            QMessageBox.information(
                self, "Не выбрано",
                "Выберите строку для удаления.",
            )
            return
        row = self._table.currentRow()
        number_item = self._table.item(row, 0)
        if number_item is None:
            return
        number = int(number_item.text())
        self._service.remove_point(number)
        self._refresh_table()
