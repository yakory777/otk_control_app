from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SettingsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Настройки")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Пользователи, пути и базовые параметры",
        )
        subtitle.setObjectName("pageSub")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        for txt in [
            "Папка данных: data/",
            "Текущий оператор: sadasd",
            "План сборки: PyInstaller",
            "Тема: светлая промышленная",
        ]:
            card_layout.addWidget(QLabel(txt))
        card_layout.addStretch()
        layout.addWidget(card, 1)
