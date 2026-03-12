from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
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


class MeasurementsPage(QWidget):
    def __init__(self, service: ProjectService) -> None:
        super().__init__()
        project = service.current_project()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Измерения")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Тестовый экран ввода измерений")
        subtitle.setObjectName("pageSub")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        body = QHBoxLayout()

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        table = QTableWidget(4, 6)
        table.setAlternatingRowColors(True)
        table.setHorizontalHeaderLabels([
            "№", "Размер", "Истинное",
            "Измерено", "Отклонение", "Статус",
        ])
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch,
        )
        table.verticalHeader().setVisible(False)

        rows = [
            ["1", "Диаметр D1", "25.000",
             "25.012", "+0.012", "Норма"],
            ["2", "Длина L2", "84.500",
             "84.471", "-0.029", "Норма"],
            ["3", "Отверстие H3", "8.214",
             "8.214", "+0.014", "Внимание"],
            ["4", "Радиус R4", "3.000",
             "3.019", "+0.019", "Брак"],
        ]
        for r, row_data in enumerate(rows):
            for c, val in enumerate(row_data):
                table.setItem(r, c, QTableWidgetItem(val))

        card_layout.addWidget(table)
        body.addWidget(card, 2)

        side = QFrame()
        side.setObjectName("card")
        side_layout = QVBoxLayout(side)
        side_layout.setContentsMargins(16, 16, 16, 16)
        project_name = project.name if project else "\u2014"
        side_layout.addWidget(QLabel(f"Проект: {project_name}"))
        side_layout.addWidget(QLabel("Размеров в норме: 22"))
        side_layout.addWidget(QLabel("Предупреждений: 6"))
        side_layout.addWidget(QLabel("Брак: 3"))
        side_layout.addStretch()
        side_layout.addWidget(QPushButton("Сохранить сессию"))
        body.addWidget(side, 1)

        layout.addLayout(body, 1)
