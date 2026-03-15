from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.domain.models import STATUS_FAIL, STATUS_OK, STATUS_WARN
from app.services.export_service import ExportService
from app.services.project_service import ProjectService
from app.ui.components.stat_card import StatCard
from app.ui.pages.base_page import BasePage

logger = logging.getLogger(__name__)

try:
    from matplotlib.backends.backend_qtagg import (
        FigureCanvasQTAgg,
    )
    from matplotlib.figure import Figure
    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False


class AnalyticsPage(BasePage):
    _deviation_canvas: Any = None
    _pie_canvas: Any = None

    def __init__(
        self,
        service: ProjectService,
        export_service: ExportService,
    ) -> None:
        super().__init__(
            "Аналитика",
            "Графики, статистика и экспорт",
        )
        self._service = service
        self._export_service = export_service

        self._top = QHBoxLayout()
        self._card_total = StatCard(
            "Измерений", "0",
            "по текущему проекту",
        )
        self._card_avg = StatCard(
            "Среднее", "—",
            "среднее отклонение",
        )
        self._card_reject = StatCard(
            "Брак", "0", "выходы за допуск",
        )
        self._top.addWidget(self._card_total)
        self._top.addWidget(self._card_avg)
        self._top.addWidget(self._card_reject)
        self._root.addLayout(self._top)

        if _HAS_MATPLOTLIB:
            charts = QFrame()
            charts.setObjectName("card")
            charts_lay = QGridLayout(charts)
            self._deviation_canvas = FigureCanvasQTAgg(
                Figure(figsize=(5, 2.5)),
            )
            self._pie_canvas = FigureCanvasQTAgg(
                Figure(figsize=(3, 2.5)),
            )
            charts_lay.addWidget(
                QLabel("Отклонения по размерам"),
                0, 0, Qt.AlignmentFlag.AlignLeft,
            )
            charts_lay.addWidget(
                QLabel("Распределение статусов"),
                0, 1, Qt.AlignmentFlag.AlignLeft,
            )
            charts_lay.addWidget(self._deviation_canvas, 1, 0)
            charts_lay.addWidget(self._pie_canvas, 1, 1)
            self._root.addWidget(charts, 1)
        else:
            placeholder = QFrame()
            placeholder.setObjectName("card")
            ph_layout = QVBoxLayout(placeholder)
            lbl = QLabel(
                "Графики требуют matplotlib.\n"
                "Установите: pip install matplotlib",
            )
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ph_layout.addWidget(lbl)
            self._root.addWidget(placeholder, 1)
            self._deviation_canvas = None
            self._pie_canvas = None

        self._build_export_section()
        self.refresh()

    def _build_export_section(self) -> None:
        export_box = QFrame()
        export_box.setObjectName("card")
        lay = QVBoxLayout(export_box)
        lay.setContentsMargins(16, 12, 16, 12)

        title = QLabel("Экспорт и отчёты")
        title.setStyleSheet(
            "font-weight:700; font-size:13px;",
        )
        lay.addWidget(title)

        btns = QHBoxLayout()

        self._proto_btn = QPushButton(
            "Сформировать протокол",
        )
        self._proto_btn.setObjectName("primaryButton")
        self._proto_btn.clicked.connect(
            self._export_protocol,
        )
        btns.addWidget(self._proto_btn)

        self._pdf_btn = QPushButton("Экспорт в PDF")
        self._pdf_btn.setObjectName("primaryButton")
        self._pdf_btn.clicked.connect(
            self._export_pdf,
        )
        btns.addWidget(self._pdf_btn)

        self._xlsx_btn = QPushButton("Экспорт в Excel")
        self._xlsx_btn.setObjectName("primaryButton")
        self._xlsx_btn.clicked.connect(
            self._export_excel,
        )
        btns.addWidget(self._xlsx_btn)

        self._print_btn = QPushButton("Печать")
        self._print_btn.setObjectName("primaryButton")
        self._print_btn.clicked.connect(
            self._print_report,
        )
        btns.addWidget(self._print_btn)

        btns.addStretch()
        lay.addLayout(btns)
        self._root.addWidget(export_box)

    # ── Обновление stat cards ──

    def refresh(self) -> None:
        """Пересчитать stat cards и графики из текущего проекта."""
        project = self._service.current_project()
        if project is None:
            self._card_total.set_value("0")
            self._card_avg.set_value("—")
            self._card_reject.set_value("0")
            if _HAS_MATPLOTLIB and self._deviation_canvas:
                self._draw_empty_charts()
            return

        measured = [
            pt for pt in project.points
            if pt.measured_value
        ]
        self._card_total.set_value(str(len(measured)))

        deviations = [
            pt.deviation for pt in measured
            if pt.deviation is not None
        ]
        if deviations:
            avg = sum(
                abs(d) for d in deviations
            ) / len(deviations)
            self._card_avg.set_value(f"{avg:.4f}")
        else:
            self._card_avg.set_value("—")

        rejects = sum(
            1 for pt in measured
            if pt.status == "Брак"
        )
        self._card_reject.set_value(str(rejects))

        if _HAS_MATPLOTLIB and self._deviation_canvas:
            self._draw_deviation_chart(measured)
            self._draw_pie_chart(measured)

    def _draw_empty_charts(self) -> None:
        for fig in (self._deviation_canvas.figure, self._pie_canvas.figure):
            fig.clear()
        self._deviation_canvas.draw()
        self._pie_canvas.draw()

    def _draw_deviation_chart(self, measured: list) -> None:
        ax = self._deviation_canvas.figure.subplots()
        ax.clear()
        if not measured:
            ax.set_ylabel("Отклонение")
            self._deviation_canvas.draw()
            return
        numbers = [pt.number for pt in measured]
        devs = [
            pt.deviation if pt.deviation is not None else 0
            for pt in measured
        ]
        colors = []
        for pt in measured:
            if pt.status == STATUS_OK:
                colors.append("#10b981")
            elif pt.status == STATUS_WARN:
                colors.append("#f59e0b")
            else:
                colors.append("#ef4444")
        ax.bar(numbers, devs, color=colors, edgecolor="none")
        try:
            tp = float(measured[0].tol_plus)
            tm = float(measured[0].tol_minus)
        except (ValueError, TypeError):
            tp, tm = 0, 0
        ax.axhline(tp, color="#94a3b8", linestyle="--", linewidth=1)
        ax.axhline(tm, color="#94a3b8", linestyle="--", linewidth=1)
        ax.axhline(0, color="#64748b", linestyle="-", linewidth=0.5)
        ax.set_xlabel("№ размера")
        ax.set_ylabel("Отклонение")
        self._deviation_canvas.draw()

    def _draw_pie_chart(self, measured: list) -> None:
        ax = self._pie_canvas.figure.subplots()
        ax.clear()
        ok = sum(1 for pt in measured if pt.status == STATUS_OK)
        warn = sum(1 for pt in measured if pt.status == STATUS_WARN)
        fail = sum(1 for pt in measured if pt.status == STATUS_FAIL)
        if ok + warn + fail == 0:
            ax.text(0.5, 0.5, "Нет замеров", ha="center", va="center")
            self._pie_canvas.draw()
            return
        sizes = [ok, warn, fail]
        labels = ["Норма", "Внимание", "Брак"]
        colors = ["#10b981", "#f59e0b", "#ef4444"]
        ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct="%1.0f%%",
            startangle=90,
        )
        self._pie_canvas.draw()

    # ── Проверка проекта ──

    def _require_project(self):
        project = self._service.current_project()
        if project is None:
            QMessageBox.warning(
                self, "Нет проекта",
                "Сначала выберите проект.",
            )
            return None
        return project

    # ── Экспорт ──

    def _export_excel(self) -> None:
        project = self._require_project()
        if project is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в Excel",
            f"{project.name}.xlsx",
            "Excel (*.xlsx)",
        )
        if not path:
            return
        try:
            self._export_service.export_excel(project, path)
            QMessageBox.information(
                self, "Готово",
                f"Файл сохранён:\n{path}",
            )
        except Exception:
            logger.exception("Ошибка Excel экспорта")
            QMessageBox.critical(
                self, "Ошибка",
                "Не удалось сохранить файл.",
            )

    def _export_pdf(self) -> None:
        project = self._require_project()
        if project is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в PDF",
            f"{project.name}.pdf",
            "PDF (*.pdf)",
        )
        if not path:
            return
        try:
            self._export_service.export_pdf(project, path)
            QMessageBox.information(
                self, "Готово",
                f"PDF сохранён:\n{path}",
            )
        except Exception:
            logger.exception("Ошибка PDF экспорта")
            QMessageBox.critical(
                self, "Ошибка",
                "Не удалось сохранить PDF.",
            )

    def _export_protocol(self) -> None:
        self._export_pdf()

    def _print_report(self) -> None:
        project = self._require_project()
        if project is None:
            return
        try:
            self._export_service.print_report(
                project, self,
            )
        except Exception:
            logger.exception("Ошибка печати")
            QMessageBox.critical(
                self, "Ошибка",
                "Не удалось распечатать.",
            )
