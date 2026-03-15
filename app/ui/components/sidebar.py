from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QListWidget,
    QVBoxLayout,
    QWidget,
)


class Sidebar(QWidget):
    def __init__(self, on_change: Callable[[int], None]) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setMinimumWidth(270)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        brand = QFrame()
        brand.setObjectName("brandCard")
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(18, 18, 18, 18)

        title = QLabel("DXF Inspector")
        title.setObjectName("brandTitle")
        subtitle = QLabel(
            "Проекты, DXF, замеры, аналитика и отчеты",
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("brandSub")

        brand_layout.addWidget(title)
        brand_layout.addWidget(subtitle)
        layout.addWidget(brand)

        self.menu = QListWidget()
        self.menu.setObjectName("menu")
        self.menu.addItems([
            "Проекты",
            "Шаблон контроля",
            "Измерения",
            "Аналитика",
            "История изменений",
            "Настройки",
        ])
        self.menu.currentRowChanged.connect(on_change)
        self.menu.setCurrentRow(0)
        layout.addWidget(self.menu)
        layout.addStretch()
