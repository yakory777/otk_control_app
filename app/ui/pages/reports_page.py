from __future__ import annotations

from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout

from app.ui.pages.base_page import BasePage


class ReportsPage(BasePage):
    def __init__(self) -> None:
        super().__init__(
            "Отчеты",
            "Экспорт, печать и шаблоны протоколов",
        )

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
        self._root.addWidget(card, 1)
