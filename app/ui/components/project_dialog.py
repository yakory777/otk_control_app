from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
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
        self.dxf_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        self.desc_edit.setFixedHeight(90)

        dxf_row = QHBoxLayout()
        browse_btn = QPushButton("Обзор…")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_dxf)
        dxf_row.addWidget(self.dxf_edit)
        dxf_row.addWidget(browse_btn)

        form.addRow("Название:", self.name_edit)
        form.addRow("DXF:", dxf_row)
        form.addRow("Описание:", self.desc_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_dxf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите DXF-файл",
            "",
            "DXF-файлы (*.dxf);;Все файлы (*)",
        )
        if path:
            self.dxf_edit.setText(path)

    def data(self) -> tuple[str, str, str]:
        return (
            self.name_edit.text().strip(),
            self.dxf_edit.text().strip(),
            self.desc_edit.toPlainText().strip(),
        )
