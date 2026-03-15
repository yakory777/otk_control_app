from __future__ import annotations

import logging
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.domain.models import (
    STATUS_FAIL,
    STATUS_OK,
    STATUS_WARN,
    ControlPoint,
)
from app.services.export_service import ExportService
from app.services.project_service import ProjectService
from app.ui.pages.base_page import BasePage

logger = logging.getLogger(__name__)

_COL_NUM = 0
_COL_NAME = 1
_COL_TRUE = 2
_COL_MEASURED = 3
_COL_DEVIATION = 4
_COL_STATUS = 5
_COLUMN_COUNT = 6

_STATUS_COLORS: dict[str, str] = {
    STATUS_OK: "color: #047857; background: #ecfdf5;",
    STATUS_WARN: "color: #b45309; background: #fffbeb;",
    STATUS_FAIL: "color: #be123c; background: #fff1f2;",
}


class MeasurementsPage(BasePage):
    """Страница ввода измерений с реальными данными."""

    def __init__(
        self,
        service: ProjectService,
        export_service: ExportService,
    ) -> None:
        super().__init__(
            "Измерения",
            "Ввод замеров и контроль отклонений",
        )
        self._service = service
        self._export_service = export_service
        self._points: list[ControlPoint] = []
        self._updating = False

        body = QHBoxLayout()
        self._build_table(body)
        self._build_summary(body)
        self._root.addLayout(body, 1)

        self.refresh()

    def _build_table(self, parent: QHBoxLayout) -> None:
        card = QFrame()
        card.setObjectName("card")
        card_lay = QVBoxLayout(card)

        self._table = QTableWidget(0, _COLUMN_COUNT)
        self._table.setAlternatingRowColors(True)
        self._table.setHorizontalHeaderLabels([
            "№", "Размер", "Истинное",
            "Измерено", "Отклонение", "Статус",
        ])
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.cellChanged.connect(
            self._on_cell_changed,
        )
        card_lay.addWidget(self._table)
        parent.addWidget(card, 2)

    def _build_summary(
        self, parent: QHBoxLayout,
    ) -> None:
        side = QFrame()
        side.setObjectName("card")
        side_lay = QVBoxLayout(side)
        side_lay.setContentsMargins(16, 16, 16, 16)

        self._project_lbl = QLabel("Проект: —")
        self._project_lbl.setStyleSheet(
            "font-weight: 600; font-size: 14px;",
        )
        side_lay.addWidget(self._project_lbl)

        side_lay.addSpacing(12)

        self._ok_lbl = self._stat_row(
            side_lay, "Размеров в норме",
            "font-weight: 600; color: #047857;",
        )
        self._warn_lbl = self._stat_row(
            side_lay, "Предупреждений",
            "font-weight: 600; color: #b45309;",
        )
        self._fail_lbl = self._stat_row(
            side_lay, "Брак",
            "font-weight: 600; color: #be123c;",
        )

        side_lay.addStretch()

        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._on_save)
        print_btn = QPushButton("Печать")
        print_btn.clicked.connect(self._on_print)

        side_lay.addWidget(save_btn)
        side_lay.addWidget(print_btn)
        parent.addWidget(side, 1)

    @staticmethod
    def _stat_row(
        parent: QVBoxLayout,
        label_text: str,
        value_style: str,
    ) -> QLabel:
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet(
            "color: #64748b; font-size: 13px;",
        )
        val = QLabel("0")
        val.setStyleSheet(value_style)
        val.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )
        row.addWidget(lbl)
        row.addWidget(val)
        parent.addLayout(row)
        return val

    # ── Обновление данных ──

    def refresh(self) -> None:
        """Пересобрать таблицу из текущего проекта."""
        logger.debug("Обновление MeasurementsPage")
        project = self._service.current_project()
        if not project:
            self._project_lbl.setText("Проект: —")
            self._points = []
            self._table.setRowCount(0)
            self._update_summary()
            return

        self._project_lbl.setText(
            f"Проект: {project.name}",
        )
        self._points = project.points
        self._rebuild_table()
        self._update_summary()

    def _rebuild_table(self) -> None:
        self._updating = True
        self._table.setRowCount(len(self._points))
        for row, pt in enumerate(self._points):
            self._set_readonly(
                row, _COL_NUM, str(pt.number),
            )
            self._set_readonly(row, _COL_NAME, pt.name)
            self._set_readonly(
                row, _COL_TRUE, pt.true_value,
            )

            measured_item = QTableWidgetItem(
                pt.measured_value,
            )
            self._table.setItem(
                row, _COL_MEASURED, measured_item,
            )

            dev = pt.deviation
            dev_text = (
                f"{dev:+.3f}" if dev is not None else ""
            )
            self._set_readonly(
                row, _COL_DEVIATION, dev_text,
            )

            status_item = QTableWidgetItem(pt.status)
            status_item.setFlags(
                status_item.flags()
                & ~Qt.ItemFlag.ItemIsEditable
            )
            self._table.setItem(
                row, _COL_STATUS, status_item,
            )
            self._style_status_cell(row, pt.status)

        self._updating = False

    def _set_readonly(
        self, row: int, col: int, text: str,
    ) -> None:
        item = QTableWidgetItem(text)
        item.setFlags(
            item.flags() & ~Qt.ItemFlag.ItemIsEditable
        )
        self._table.setItem(row, col, item)

    def _style_status_cell(
        self, row: int, status: str,
    ) -> None:
        item = self._table.item(row, _COL_STATUS)
        if item is None:
            return
        style = _STATUS_COLORS.get(status, "")
        if style:
            parts = style.split(";")
            for part in parts:
                part = part.strip()
                if part.startswith("color:"):
                    color_val = part.split(":")[1].strip()
                    item.setForeground(QColor(color_val))

    def _on_cell_changed(
        self, row: int, col: int,
    ) -> None:
        if self._updating:
            return
        if col != _COL_MEASURED:
            return
        if row >= len(self._points):
            return
        item = self._table.item(row, col)
        if item is None:
            return
        value = item.text().strip()
        pt = self._points[row]
        pt.measured_value = value
        logger.debug(
            "Замер обновлён: #%d = %s", pt.number, value,
        )

        self._updating = True
        dev = pt.deviation
        dev_text = (
            f"{dev:+.3f}" if dev is not None else ""
        )
        dev_item = self._table.item(row, _COL_DEVIATION)
        if dev_item:
            dev_item.setText(dev_text)

        status_item = self._table.item(row, _COL_STATUS)
        if status_item:
            status_item.setText(pt.status)
        self._style_status_cell(row, pt.status)
        self._updating = False

        self._update_summary()

    def _on_save(self) -> None:
        project = self._service.current_project()
        if not project:
            QMessageBox.warning(
                self, "Нет проекта",
                "Сначала выберите проект.",
            )
            return
        for pt in self._points:
            self._service.update_point(
                project.project_id,
                pt.number,
                pt.name,
                pt.kind,
                pt.true_value,
                pt.tol_plus,
                pt.tol_minus,
                x=pt.x,
                y=pt.y,
                entity_handle=pt.entity_handle,
                measured_value=pt.measured_value,
            )
        today = date.today().strftime("%d.%m.%Y")
        self._service.update_last_control(
            project.project_id,
            today,
        )
        QMessageBox.information(
            self, "Сохранено",
            "Замеры сохранены.",
        )

    def _on_print(self) -> None:
        project = self._service.current_project()
        if not project:
            QMessageBox.warning(
                self, "Нет проекта",
                "Сначала выберите проект.",
            )
            return
        try:
            self._export_service.print_report(project, self)
        except Exception:
            logger.exception("Ошибка печати")
            QMessageBox.critical(
                self, "Ошибка",
                "Не удалось распечатать.",
            )

    def _update_summary(self) -> None:
        ok = warn = fail = 0
        for pt in self._points:
            s = pt.status
            if s == STATUS_OK:
                ok += 1
            elif s == STATUS_WARN:
                warn += 1
            elif s == STATUS_FAIL:
                fail += 1
        self._ok_lbl.setText(str(ok))
        self._warn_lbl.setText(str(warn))
        self._fail_lbl.setText(str(fail))
