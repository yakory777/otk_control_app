from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class StatCard(QFrame):
    def __init__(self, title: str, value: str, note: str) -> None:
        super().__init__()
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("statTitle")
        self._lbl_value = QLabel(value)
        self._lbl_value.setObjectName("statValue")
        lbl_note = QLabel(note)
        lbl_note.setObjectName("statNote")

        layout.addWidget(lbl_title)
        layout.addWidget(self._lbl_value)
        layout.addWidget(lbl_note)

    def set_value(self, value: str) -> None:
        """Обновить отображаемое значение."""
        self._lbl_value.setText(value)
