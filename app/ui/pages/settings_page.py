# app/ui/pages/settings_page.py

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.domain.models import AppConfig
from app.services.config_service import ConfigService
from app.ui.pages.base_page import BasePage


class SettingsPage(BasePage):
    """Страница настроек приложения."""

    def __init__(self, config_service: ConfigService) -> None:
        super().__init__(
            "Настройки",
            "Папка данных, оператор и тема",
        )
        self._config_service = config_service
        self._config = config_service.load()

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)

        form = QFormLayout()

        self._data_dir_edit = QLineEdit()
        self._data_dir_edit.setPlaceholderText("data")
        self._data_dir_edit.setText(self._config.data_dir)
        browse_btn = QPushButton("Обзор…")
        browse_btn.clicked.connect(self._browse_data_dir)
        data_dir_row = QWidget()
        data_dir_lay = QHBoxLayout(data_dir_row)
        data_dir_lay.setContentsMargins(0, 0, 0, 0)
        data_dir_lay.addWidget(self._data_dir_edit)
        data_dir_lay.addWidget(browse_btn)
        form.addRow("Папка данных:", data_dir_row)

        self._operator_edit = QLineEdit()
        self._operator_edit.setPlaceholderText("Имя оператора ОТК")
        self._operator_edit.setText(self._config.operator)
        form.addRow("Оператор:", self._operator_edit)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["light", "dark"])
        idx = self._theme_combo.findText(
            self._config.theme,
        )
        if idx >= 0:
            self._theme_combo.setCurrentIndex(idx)
        form.addRow("Тема:", self._theme_combo)

        card_layout.addLayout(form)

        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._on_save)
        card_layout.addWidget(save_btn)
        card_layout.addStretch()

        self._root.addWidget(card, 1)

    def _browse_data_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку данных",
            self._data_dir_edit.text() or ".",
        )
        if path:
            self._data_dir_edit.setText(Path(path).as_posix())

    def _on_save(self) -> None:
        self._config = AppConfig(
            data_dir=self._data_dir_edit.text().strip() or "data",
            operator=self._operator_edit.text().strip(),
            theme=self._theme_combo.currentText(),
            db_path=self._config.db_path,
        )
        self._config_service.save(self._config)
        QMessageBox.information(
            self,
            "Сохранено",
            "Настройки сохранены.",
        )
