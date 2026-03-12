from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)


class PointDialog(QDialog):
    """Диалог добавления контрольного размера (точки)."""

    KINDS = ["Диаметр", "Линейный", "Радиус", "Угол", "Другое"]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Добавить размер")
        self.resize(360, 260)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Например: Диаметр D1")

        self.kind_combo = QComboBox()
        self.kind_combo.addItems(self.KINDS)

        self.true_edit = QLineEdit()
        self.true_edit.setPlaceholderText("0.000")

        self.plus_edit = QLineEdit()
        self.plus_edit.setPlaceholderText("+0.000")

        self.minus_edit = QLineEdit()
        self.minus_edit.setPlaceholderText("-0.000")

        form.addRow("Название:", self.name_edit)
        form.addRow("Тип:", self.kind_combo)
        form.addRow("Истинное значение:", self.true_edit)
        form.addRow("Допуск +:", self.plus_edit)
        form.addRow("Допуск −:", self.minus_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def data(self) -> tuple[str, str, str, str, str]:
        """Возвращает (name, kind, true_value, tol_plus, tol_minus)."""
        return (
            self.name_edit.text().strip(),
            self.kind_combo.currentText(),
            self.true_edit.text().strip() or "0.000",
            self.plus_edit.text().strip() or "+0.000",
            self.minus_edit.text().strip() or "-0.000",
        )
