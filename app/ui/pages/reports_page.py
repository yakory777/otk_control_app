from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ReportsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Отчеты")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Экспорт, печать и шаблоны протоколов",
        )
        subtitle.setObjectName("pageSub")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.addWidget(
            QPushButton("Сформировать протокол"),
        )
        card_layout.addWidget(QPushButton("Экспорт в PDF"))
        card_layout.addWidget(QPushButton("Экспорт в Excel"))
        card_layout.addWidget(QPushButton("Печать"))
        card_layout.addStretch()
        layout.addWidget(card, 1)
