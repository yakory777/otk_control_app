from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class BasePage(QWidget):
    """Базовый класс страницы с заголовком и подзаголовком."""

    def __init__(
        self,
        title: str,
        subtitle: str,
    ) -> None:
        super().__init__()
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(24, 24, 24, 24)
        self._root.setSpacing(16)

        self._title_lbl = QLabel(title)
        self._title_lbl.setObjectName("pageTitle")
        self._sub_lbl = QLabel(subtitle)
        self._sub_lbl.setObjectName("pageSub")
        self._root.addWidget(self._title_lbl)
        self._root.addWidget(self._sub_lbl)
