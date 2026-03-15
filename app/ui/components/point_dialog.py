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

from app.domain.dxf_entities import DxfEntityInfo
from app.domain.models import ControlPoint


class PointDialog(QDialog):
    """Диалог добавления / редактирования размера."""

    KINDS = [
        "Диаметр", "Линейный", "Радиус",
        "Угол", "Другое",
    ]

    def __init__(
        self,
        parent: QWidget | None = None,
        prefill: DxfEntityInfo | None = None,
        edit_point: ControlPoint | None = None,
    ) -> None:
        super().__init__(parent)
        editing = edit_point is not None
        self.setWindowTitle(
            "Редактировать размер"
            if editing
            else "Добавить размер",
        )
        self.resize(400, 280)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(
            "Например: Диаметр D1",
        )

        self.kind_combo = QComboBox()
        self.kind_combo.addItems(self.KINDS)

        self.true_edit = QLineEdit()
        self.true_edit.setPlaceholderText("0.000")

        self.plus_edit = QLineEdit()
        self.plus_edit.setPlaceholderText("+0.000")

        self.minus_edit = QLineEdit()
        self.minus_edit.setPlaceholderText("-0.000")

        if editing and edit_point is not None:
            self.name_edit.setText(edit_point.name)
            if edit_point.kind in self.KINDS:
                self.kind_combo.setCurrentText(
                    edit_point.kind,
                )
            self.true_edit.setText(edit_point.true_value)
            self.plus_edit.setText(edit_point.tol_plus)
            self.minus_edit.setText(edit_point.tol_minus)
        elif prefill is not None:
            if prefill.kind in self.KINDS:
                self.kind_combo.setCurrentText(
                    prefill.kind,
                )
            self.true_edit.setText(prefill.value)

        form.addRow("Название:", self.name_edit)
        form.addRow("Тип:", self.kind_combo)
        form.addRow("Истинное значение:", self.true_edit)
        form.addRow("Допуск +:", self.plus_edit)
        form.addRow("Допуск −:", self.minus_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def data(self) -> tuple[str, str, str, str, str]:
        """(name, kind, true_value, tol_plus, tol_minus)."""
        return (
            self.name_edit.text().strip(),
            self.kind_combo.currentText(),
            self.true_edit.text().strip() or "0.000",
            self.plus_edit.text().strip() or "+0.000",
            self.minus_edit.text().strip() or "-0.000",
        )
