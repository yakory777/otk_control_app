from __future__ import annotations

from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class HistoryPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("История изменений")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Журнал изменений истинных значений и действий",
        )
        subtitle.setObjectName("pageSub")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        table = QTableWidget(3, 5)
        table.setAlternatingRowColors(True)
        table.setHorizontalHeaderLabels([
            "Дата", "Пользователь", "Размер",
            "Старое", "Новое",
        ])
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch,
        )
        table.verticalHeader().setVisible(False)

        rows = [
            ["12.03.2026 09:40", "sadasd",
             "Диаметр D1", "24.998", "25.000"],
            ["11.03.2026 15:10", "sadasd",
             "Радиус R4", "2.995", "3.000"],
            ["10.03.2026 10:05", "sadasd",
             "Длина L2", "84.480", "84.500"],
        ]
        for r, row_data in enumerate(rows):
            for c, val in enumerate(row_data):
                table.setItem(r, c, QTableWidgetItem(val))

        layout.addWidget(table, 1)
