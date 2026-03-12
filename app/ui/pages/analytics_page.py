from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.ui.components.stat_card import StatCard


class AnalyticsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Аналитика")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Графики и статистика по отклонениям",
        )
        subtitle.setObjectName("pageSub")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        top = QHBoxLayout()
        top.addWidget(
            StatCard("Измерений", "28", "по текущему проекту"),
        )
        top.addWidget(
            StatCard("Среднее", "0.0035", "среднее отклонение"),
        )
        top.addWidget(
            StatCard("Брак", "3", "выходы за допуск"),
        )
        layout.addLayout(top)

        placeholder = QFrame()
        placeholder.setObjectName("card")
        ph_layout = QVBoxLayout(placeholder)
        lbl = QLabel(
            "Здесь будут реальные графики.\n"
            "В этой сборке раздел уже присутствует"
            " и не пустой."
        )
        lbl.setAlignment(Qt.AlignCenter)
        ph_layout.addWidget(lbl)
        layout.addWidget(placeholder, 1)
