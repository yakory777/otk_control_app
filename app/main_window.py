from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from app.state import AppState, Project

STYLE = """
QMainWindow { background: #f1f5f9; }
QWidget { color: #0f172a; font-size: 14px; }
#sidebar { background: #f8fafc; border-right: 1px solid #e2e8f0; }
#brandCard { background: #0f172a; border-radius: 22px; }
#brandTitle { color: white; font-size: 24px; font-weight: 700; }
#brandSub { color: #cbd5e1; font-size: 12px; }
#menu { background: transparent; border: none; }
#menu::item { background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 14px 16px; margin: 4px 0; font-weight: 600; }
#menu::item:selected { background: #0f172a; color: white; border: 1px solid #0f172a; }
#card { background: white; border: 1px solid #e2e8f0; border-radius: 20px; }
#pageTitle { font-size: 30px; font-weight: 700; }
#pageSub { color: #64748b; font-size: 13px; }
#statTitle { color: #64748b; font-size: 12px; }
#statValue { font-size: 28px; font-weight: 700; }
#statNote { color: #64748b; font-size: 12px; }
#primaryButton { background: #0f172a; color: white; border: 1px solid #0f172a; border-radius: 16px; padding: 11px 16px; font-weight: 700; }
#dangerButton { background: #be123c; color: white; border: 1px solid #be123c; border-radius: 16px; padding: 11px 16px; font-weight: 700; }
QPushButton { background: white; border: 1px solid #cbd5e1; border-radius: 16px; padding: 11px 16px; font-weight: 700; }
QPushButton:hover { background: #f8fafc; }
QTableWidget { background: white; border: 1px solid #e2e8f0; border-radius: 16px; gridline-color: #e2e8f0; alternate-background-color: #f8fafc; }
QHeaderView::section { background: #f8fafc; border: none; border-bottom: 1px solid #e2e8f0; padding: 10px; color: #475569; font-weight: 700; }
QGraphicsView { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; }
QGroupBox { background: white; border: 1px solid #e2e8f0; border-radius: 20px; margin-top: 8px; padding-top: 12px; font-weight: 700; }
"""


def resource_path(relative: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base = Path(getattr(sys, "_MEIPASS"))
    else:
        base = Path(__file__).resolve().parents[1]
    return str(base / relative)


class StatCard(QFrame):
    def __init__(self, title: str, value: str, note: str):
        super().__init__()
        self.setObjectName("card")
        l = QVBoxLayout(self)
        l.setContentsMargins(16, 16, 16, 16)
        t = QLabel(title)
        t.setObjectName("statTitle")
        v = QLabel(value)
        v.setObjectName("statValue")
        n = QLabel(note)
        n.setObjectName("statNote")
        l.addWidget(t)
        l.addWidget(v)
        l.addWidget(n)


class ProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новый проект")
        self.resize(420, 260)
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit()
        self.dxf = QLineEdit("data/samples/demo_part.dxf")
        self.desc = QTextEdit()
        self.desc.setFixedHeight(90)
        form.addRow("Название:", self.name)
        form.addRow("DXF:", self.dxf)
        form.addRow("Описание:", self.desc)
        lay.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        lay.addWidget(buttons)

    def data(self):
        return self.name.text().strip(), self.dxf.text().strip(), self.desc.toPlainText().strip()


class Sidebar(QWidget):
    def __init__(self, on_change):
        super().__init__()
        self.setObjectName("sidebar")
        self.setMinimumWidth(270)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        brand = QFrame()
        brand.setObjectName("brandCard")
        bl = QVBoxLayout(brand)
        bl.setContentsMargins(18, 18, 18, 18)
        t = QLabel("DXF Inspector")
        t.setObjectName("brandTitle")
        s = QLabel("Проекты, DXF, замеры, аналитика и отчеты")
        s.setWordWrap(True)
        s.setObjectName("brandSub")
        bl.addWidget(t)
        bl.addWidget(s)
        lay.addWidget(brand)
        self.menu = QListWidget()
        self.menu.setObjectName("menu")
        self.menu.addItems(["Проекты", "Шаблон контроля", "Измерения", "Аналитика", "Отчеты", "История изменений", "Настройки"])
        self.menu.currentRowChanged.connect(on_change)
        self.menu.setCurrentRow(0)
        lay.addWidget(self.menu)
        lay.addStretch()


class DxfMockView(QGraphicsView):
    def __init__(self):
        scene = QGraphicsScene()
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setSceneRect(0, 0, 820, 420)
        self._draw()

    def _draw(self):
        scene = self.scene()
        pen = QPen(QColor("#475569"))
        pen.setWidthF(2)
        helper = QPen(QColor("#94a3b8"))
        helper.setStyle(Qt.DashLine)
        scene.addRect(160, 120, 430, 170, pen)
        scene.addEllipse(230, 170, 80, 80, pen)
        scene.addEllipse(490, 185, 50, 50, pen)
        scene.addLine(160, 96, 590, 96, helper)
        scene.addLine(590, 120, 690, 120, helper)
        scene.addLine(590, 310, 690, 310, helper)
        scene.addLine(690, 120, 690, 310, helper)


class ProjectsPage(QWidget):
    def __init__(self, state: AppState, on_open_project):
        super().__init__()
        self.state = state
        self.on_open_project = on_open_project
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(16)
        self._build()
        self.refresh()

    def _build(self):
        header = QHBoxLayout()
        left = QVBoxLayout()
        t = QLabel("Панель ОТК")
        t.setObjectName("pageTitle")
        s = QLabel("Добавляйте проекты, удаляйте их и открывайте для работы")
        s.setObjectName("pageSub")
        left.addWidget(t)
        left.addWidget(s)
        header.addLayout(left)
        header.addStretch()
        self.add_btn = QPushButton("Добавить проект")
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.clicked.connect(self.add_project)
        self.del_btn = QPushButton("Удалить проект")
        self.del_btn.setObjectName("dangerButton")
        self.del_btn.clicked.connect(self.delete_project)
        header.addWidget(self.add_btn)
        header.addWidget(self.del_btn)
        self.layout.addLayout(header)

        stats = QGridLayout()
        stats.addWidget(StatCard("Проектов", "0", "активных в системе"), 0, 0)
        stats.addWidget(StatCard("Точек", "0", "контрольных размеров"), 0, 1)
        stats.addWidget(StatCard("DXF", "1", "демо-чертеж в комплекте"), 0, 2)
        stats.addWidget(StatCard("Статус", "MVP", "готов к тесту"), 0, 3)
        self.layout.addLayout(stats)

        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 16, 16, 16)
        self.table = QTableWidget(0, 5)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalHeaderLabels(["ID", "Проект", "DXF", "Описание", "Последний контроль"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.cellDoubleClicked.connect(self.open_selected)
        cl.addWidget(self.table)
        open_btn = QPushButton("Открыть выбранный проект")
        open_btn.clicked.connect(self.open_current)
        cl.addWidget(open_btn)
        self.layout.addWidget(card, 1)

    def refresh(self):
        self.table.setRowCount(len(self.state.projects))
        total_points = 0
        for r, p in enumerate(self.state.projects):
            total_points += len(p.points)
            vals = [str(p.project_id), p.name, p.dxf_file, p.description, p.last_control]
            for c, v in enumerate(vals):
                self.table.setItem(r, c, QTableWidgetItem(v))
        if self.state.projects:
            self.table.selectRow(0)
        stats = self.findChildren(StatCard)
        if len(stats) >= 2:
            stats[0].findChildren(QLabel)[1].setText(str(len(self.state.projects)))
            stats[1].findChildren(QLabel)[1].setText(str(total_points))

    def selected_project(self) -> Project | None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.state.projects):
            return None
        return self.state.projects[row]

    def add_project(self):
        dlg = ProjectDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        name, dxf, desc = dlg.data()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название проекта")
            return
        self.state.add_project(name, dxf, desc)
        self.refresh()

    def delete_project(self):
        project = self.selected_project()
        if not project:
            QMessageBox.warning(self, "Нет выбора", "Выберите проект")
            return
        ans = QMessageBox.question(self, "Удаление", f"Удалить проект '{project.name}'?")
        if ans != QMessageBox.Yes:
            return
        self.state.delete_project(project.project_id)
        self.refresh()

    def open_current(self):
        project = self.selected_project()
        if project:
            self.on_open_project(project)

    def open_selected(self, row: int, col: int):
        self.open_current()


class TemplatePage(QWidget):
    def __init__(self, state: AppState):
        super().__init__()
        self.state = state
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        head = QHBoxLayout()
        left = QVBoxLayout()
        self.title = QLabel("Шаблон контроля")
        self.title.setObjectName("pageTitle")
        self.sub = QLabel("DXF viewer, контрольные точки и свойства проекта")
        self.sub.setObjectName("pageSub")
        left.addWidget(self.title)
        left.addWidget(self.sub)
        head.addLayout(left)
        head.addStretch()
        head.addWidget(QPushButton("Добавить размер"))
        head.addWidget(QPushButton("Удалить размер"))
        lay.addLayout(head)
        splitter = QHBoxLayout()
        left_card = QGroupBox("Проект")
        ll = QVBoxLayout(left_card)
        self.info = QLabel("")
        self.info.setWordWrap(True)
        ll.addWidget(self.info)
        ll.addStretch()
        center = QGroupBox("DXF Viewer")
        cl = QVBoxLayout(center)
        cl.addWidget(DxfMockView())
        right = QGroupBox("Контрольные точки")
        rl = QVBoxLayout(right)
        self.table = QTableWidget(0, 6)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalHeaderLabels(["№", "Название", "Тип", "Истинное", "+", "-"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        rl.addWidget(self.table)
        splitter.addWidget(left_card, 1)
        splitter.addWidget(center, 2)
        splitter.addWidget(right, 2)
        lay.addLayout(splitter, 1)
        self.refresh()

    def refresh(self):
        project = self.state.current_project()
        if not project:
            self.info.setText("Нет выбранного проекта")
            self.table.setRowCount(0)
            return
        self.info.setText(f"Проект: {project.name}\nDXF: {project.dxf_file}\nОписание: {project.description}\nПоследний контроль: {project.last_control}")
        self.table.setRowCount(len(project.points))
        for r, p in enumerate(project.points):
            vals = [str(p.number), p.name, p.kind, p.true_value, p.tol_plus, p.tol_minus]
            for c, v in enumerate(vals):
                self.table.setItem(r, c, QTableWidgetItem(v))


class MeasurementsPage(QWidget):
    def __init__(self, state: AppState):
        super().__init__()
        project = state.current_project()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        t = QLabel("Измерения")
        t.setObjectName("pageTitle")
        s = QLabel("Тестовый экран ввода измерений")
        s.setObjectName("pageSub")
        lay.addWidget(t)
        lay.addWidget(s)
        body = QHBoxLayout()
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        table = QTableWidget(4, 6)
        table.setAlternatingRowColors(True)
        table.setHorizontalHeaderLabels(["№", "Размер", "Истинное", "Измерено", "Отклонение", "Статус"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        rows = [["1", "Диаметр D1", "25.000", "25.012", "+0.012", "Норма"], ["2", "Длина L2", "84.500", "84.471", "-0.029", "Норма"], ["3", "Отверстие H3", "8.214", "8.214", "+0.014", "Внимание"], ["4", "Радиус R4", "3.000", "3.019", "+0.019", "Брак"]]
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                table.setItem(r, c, QTableWidgetItem(v))
        cl.addWidget(table)
        body.addWidget(card, 2)
        side = QFrame()
        side.setObjectName("card")
        sl = QVBoxLayout(side)
        sl.setContentsMargins(16, 16, 16, 16)
        sl.addWidget(QLabel(f"Проект: {project.name if project else '—'}"))
        sl.addWidget(QLabel("Размеров в норме: 22"))
        sl.addWidget(QLabel("Предупреждений: 6"))
        sl.addWidget(QLabel("Брак: 3"))
        sl.addStretch()
        sl.addWidget(QPushButton("Сохранить сессию"))
        body.addWidget(side, 1)
        lay.addLayout(body, 1)


class AnalyticsPage(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        t = QLabel("Аналитика")
        t.setObjectName("pageTitle")
        s = QLabel("Графики и статистика по отклонениям")
        s.setObjectName("pageSub")
        lay.addWidget(t)
        lay.addWidget(s)
        top = QHBoxLayout()
        top.addWidget(StatCard("Измерений", "28", "по текущему проекту"))
        top.addWidget(StatCard("Среднее", "0.0035", "среднее отклонение"))
        top.addWidget(StatCard("Брак", "3", "выходы за допуск"))
        lay.addLayout(top)
        ph = QFrame()
        ph.setObjectName("card")
        pl = QVBoxLayout(ph)
        lab = QLabel("Здесь будут реальные графики.\nВ этой сборке раздел уже присутствует и не пустой.")
        lab.setAlignment(Qt.AlignCenter)
        pl.addWidget(lab)
        lay.addWidget(ph, 1)


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        t = QLabel("Отчеты")
        t.setObjectName("pageTitle")
        s = QLabel("Экспорт, печать и шаблоны протоколов")
        s.setObjectName("pageSub")
        lay.addWidget(t)
        lay.addWidget(s)
        card = QFrame(); card.setObjectName("card")
        cl = QVBoxLayout(card); cl.setContentsMargins(16,16,16,16)
        cl.addWidget(QPushButton("Сформировать протокол"))
        cl.addWidget(QPushButton("Экспорт в PDF"))
        cl.addWidget(QPushButton("Экспорт в Excel"))
        cl.addWidget(QPushButton("Печать"))
        cl.addStretch()
        lay.addWidget(card, 1)


class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        t = QLabel("История изменений")
        t.setObjectName("pageTitle")
        s = QLabel("Журнал изменений истинных значений и действий")
        s.setObjectName("pageSub")
        lay.addWidget(t)
        lay.addWidget(s)
        table = QTableWidget(3, 5)
        table.setAlternatingRowColors(True)
        table.setHorizontalHeaderLabels(["Дата", "Пользователь", "Размер", "Старое", "Новое"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        rows = [["12.03.2026 09:40", "sadasd", "Диаметр D1", "24.998", "25.000"], ["11.03.2026 15:10", "sadasd", "Радиус R4", "2.995", "3.000"], ["10.03.2026 10:05", "sadasd", "Длина L2", "84.480", "84.500"]]
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                table.setItem(r, c, QTableWidgetItem(v))
        lay.addWidget(table, 1)


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        t = QLabel("Настройки")
        t.setObjectName("pageTitle")
        s = QLabel("Пользователи, пути и базовые параметры")
        s.setObjectName("pageSub")
        lay.addWidget(t)
        lay.addWidget(s)
        card = QFrame(); card.setObjectName("card")
        cl = QVBoxLayout(card); cl.setContentsMargins(16,16,16,16)
        for txt in ["Папка данных: data/", "Текущий оператор: sadasd", "План сборки: PyInstaller", "Тема: светлая промышленная"]:
            cl.addWidget(QLabel(txt))
        cl.addStretch()
        lay.addWidget(card, 1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = AppState()
        self.setWindowTitle("OTK DXF Inspector")
        self.resize(1680, 960)
        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.sidebar = Sidebar(self.switch_page)
        root.addWidget(self.sidebar)
        self.pages = QStackedWidget()
        self.projects = ProjectsPage(self.state, self.open_project)
        self.template = TemplatePage(self.state)
        self.measurements = MeasurementsPage(self.state)
        self.analytics = AnalyticsPage()
        self.reports = ReportsPage()
        self.history = HistoryPage()
        self.settings = SettingsPage()
        for page in [self.projects, self.template, self.measurements, self.analytics, self.reports, self.history, self.settings]:
            self.pages.addWidget(page)
        root.addWidget(self.pages, 1)
        self.setCentralWidget(central)
        self.setStyleSheet(STYLE)

    def switch_page(self, index: int):
        if index == 1:
            self.template.refresh()
        self.pages.setCurrentIndex(index)

    def open_project(self, project: Project):
        self.state.current_project_id = project.project_id
        self.template.refresh()
        self.sidebar.menu.setCurrentRow(1)
        self.pages.setCurrentWidget(self.template)


def run_app():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
