from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ProjectDialog(QDialog):
    """Диалог создания нового проекта."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Новый проект")
        self.resize(420, 260)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.dxf_edit = QLineEdit("data/samples/demo_part.dxf")
        self.desc_edit = QTextEdit()
        self.desc_edit.setFixedHeight(90)

        form.addRow("Название:", self.name_edit)
        form.addRow("DXF:", self.dxf_edit)
        form.addRow("Описание:", self.desc_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def data(self) -> tuple[str, str, str]:
        return (
            self.name_edit.text().strip(),
            self.dxf_edit.text().strip(),
            self.desc_edit.toPlainText().strip(),
        )
