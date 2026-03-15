from __future__ import annotations

import logging
from typing import Sequence

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.domain.dxf_entities import DxfEntityInfo
from app.domain.models import ControlPoint
from app.services.project_service import ProjectService
from app.ui.components.dxf_view import DxfView
from app.ui.components.point_card import PointCard
from app.ui.components.point_dialog import PointDialog
from app.ui.pages.base_page import BasePage

logger = logging.getLogger(__name__)


class TemplatePage(BasePage):
    def __init__(self, service: ProjectService) -> None:
        super().__init__(
            "Шаблон контроля",
            "Редактор контрольных размеров",
        )
        self._service = service
        self._loaded_dxf: str | None = None
        self._selected_point: ControlPoint | None = (
            None
        )
        self._point_cards: list[PointCard] = []
        self._layer_checkboxes: dict[str, QCheckBox] = {}

        body = QHBoxLayout()
        self._build_viewer_column(body)
        self._build_right_column(body)
        self._root.addLayout(body, 1)

        self.refresh()

    # ── Построение UI ──

    def _build_viewer_column(
        self,
        parent: QHBoxLayout,
    ) -> None:
        col = QVBoxLayout()

        info_bar = QHBoxLayout()
        info_bar.setSpacing(16)
        self._prj_name_lbl = QLabel("—")
        self._prj_name_lbl.setStyleSheet(
            "font-weight:700; font-size:13px;",
        )
        self._prj_dxf_lbl = QLabel("")
        self._prj_dxf_lbl.setStyleSheet(
            "color:#94a3b8; font-size:11px;",
        )
        info_bar.addWidget(self._prj_name_lbl)
        info_bar.addWidget(self._prj_dxf_lbl, 1)
        col.addLayout(info_bar)

        self._layers_frame = QFrame()
        self._layers_frame.setObjectName("card")
        layers_main = QVBoxLayout(self._layers_frame)
        layers_main.setContentsMargins(8, 8, 8, 8)
        layers_lbl = QLabel("Слои")
        layers_lbl.setStyleSheet(
            "font-weight:700; font-size:11px; color:#94a3b8;",
        )
        layers_main.addWidget(layers_lbl)
        self._layers_inner = QWidget()
        self._layers_inner_layout = QVBoxLayout(self._layers_inner)
        self._layers_inner_layout.setContentsMargins(0, 0, 0, 0)
        self._layers_inner_layout.setSpacing(2)
        layers_scroll = QScrollArea()
        layers_scroll.setWidgetResizable(True)
        layers_scroll.setFrameShape(QFrame.Shape.NoFrame)
        layers_scroll.setMaximumHeight(120)
        layers_scroll.setWidget(self._layers_inner)
        layers_main.addWidget(layers_scroll)
        col.addWidget(self._layers_frame)
        self._layers_frame.setVisible(False)

        self._dxf_view = DxfView()
        col.addWidget(self._dxf_view, 1)

        btns = QHBoxLayout()
        self._add_btn = QPushButton("Добавить размер")
        self._add_btn.setObjectName("primaryButton")
        self._add_btn.clicked.connect(self._add_point)

        self._renum_btn = QPushButton(
            "Перенумеровать",
        )
        self._renum_btn.clicked.connect(
            self._renumber_points,
        )
        btns.addWidget(self._add_btn)
        btns.addWidget(self._renum_btn)
        btns.addStretch()
        col.addLayout(btns)

        parent.addLayout(col, 3)

    def _build_right_column(
        self,
        parent: QHBoxLayout,
    ) -> None:
        col = QVBoxLayout()
        col.setSpacing(8)

        # --- список размеров ---
        pts_lbl = QLabel("Контрольные размеры")
        pts_lbl.setStyleSheet(
            "font-weight:700; font-size:12px;",
        )
        col.addWidget(pts_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._cards_container = QVBoxLayout()
        self._cards_container.setContentsMargins(
            0, 0, 0, 0,
        )
        self._cards_container.setSpacing(4)
        self._cards_container.addStretch()
        container = QFrame()
        container.setLayout(self._cards_container)
        scroll.setWidget(container)
        col.addWidget(scroll, 1)

        # --- свойства выбранного ---
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#334155;")
        col.addWidget(sep)

        self._props_grid = QGridLayout()
        self._props_grid.setSpacing(4)
        self._props_grid.setContentsMargins(0, 0, 0, 0)

        self._prop_labels: dict[str, QLabel] = {}
        fields = [
            "Номер", "Тип", "Истинное",
            "Допуск +", "Допуск −",
        ]
        for i, name in enumerate(fields):
            row, col_idx = divmod(i, 2)
            key_lbl = QLabel(name)
            key_lbl.setStyleSheet(
                "color:#64748b; font-size:10px;"
                "padding:0; margin:0;",
            )
            val_lbl = QLabel("—")
            val_lbl.setStyleSheet(
                "font-weight:600; font-size:11px;"
                "padding:0; margin:0;",
            )
            sub = QVBoxLayout()
            sub.setSpacing(0)
            sub.setContentsMargins(4, 2, 4, 2)
            sub.addWidget(key_lbl)
            sub.addWidget(val_lbl)
            self._prop_labels[name] = val_lbl
            self._props_grid.addLayout(
                sub, row, col_idx,
            )

        col.addLayout(self._props_grid)

        parent.addLayout(col, 1)

    # ── Обновление данных ──

    def refresh(self) -> None:
        """Обновить страницу при смене проекта."""
        logger.debug("Обновление TemplatePage")
        project = self._service.current_project()
        if not project:
            self._prj_name_lbl.setText("—")
            self._prj_dxf_lbl.setText("")
            self._clear_cards()
            self._loaded_dxf = None
            self._dxf_view.clear_markers()
            return

        self._prj_name_lbl.setText(project.name)
        dxf_short = (
            project.dxf_file.rsplit("/", 1)[-1]
            if project.dxf_file else "—"
        )
        self._prj_dxf_lbl.setText(dxf_short)
        if not project.dxf_file:
            self._loaded_dxf = None
            self._layers_frame.setVisible(False)

        if (
            project.dxf_file
            and project.dxf_file != self._loaded_dxf
        ):
            self._dxf_view.load_file(project.dxf_file)
            self._loaded_dxf = project.dxf_file
            self._try_auto_import(project)

        self._refresh_layers_panel()
        self._refresh_points()

    def _refresh_layers_panel(self) -> None:
        """Обновить панель слоёв: показ/скрытие и список чекбоксов."""
        if not self._loaded_dxf:
            self._layers_frame.setVisible(False)
            return
        layers = self._dxf_view.get_available_layers()
        if not layers or len(layers) <= 1:
            self._layers_frame.setVisible(False)
            return
        self._layers_frame.setVisible(True)
        for cb in self._layer_checkboxes.values():
            cb.stateChanged.disconnect(self._on_layer_toggled)
        self._layer_checkboxes.clear()
        while self._layers_inner_layout.count():
            item = self._layers_inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._dxf_view.set_visible_layers(None)
        for name in layers:
            cb = QCheckBox(name)
            cb.setChecked(True)
            cb.stateChanged.connect(self._on_layer_toggled)
            self._layers_inner_layout.addWidget(cb)
            self._layer_checkboxes[name] = cb

    def _on_layer_toggled(self) -> None:
        """Пересчитать видимые слои и обновить вид."""
        visible = frozenset(
            name
            for name, cb in self._layer_checkboxes.items()
            if cb.isChecked()
        )
        if visible == frozenset(self._layer_checkboxes):
            self._dxf_view.set_visible_layers(None)
        else:
            self._dxf_view.set_visible_layers(visible)

    def _refresh_points(self) -> None:
        """Пересоздать карточки и маркеры."""
        project = self._service.current_project()
        if not project:
            self._clear_cards()
            self._dxf_view.clear_markers()
            return

        self._rebuild_cards(project.points)
        self._dxf_view.set_point_markers(
            project.points,
            on_marker_context_menu=self._show_marker_context_menu,
        )

        if self._selected_point is not None:
            still_exists = any(
                p.number == self._selected_point.number
                for p in project.points
            )
            if not still_exists:
                self._selected_point = None
        self._update_props()

    def _clear_cards(self) -> None:
        for card in self._point_cards:
            card.setParent(None)
            card.deleteLater()
        self._point_cards.clear()

    def _rebuild_cards(
        self,
        points: Sequence[ControlPoint],
    ) -> None:
        self._clear_cards()
        for pt in points:
            card = PointCard(
                pt,
                self._on_card_clicked,
                on_dbl_click=self._on_card_dbl_clicked,
                on_edit=self._edit_point_for,
                on_delete=self._delete_point_for,
            )
            idx = self._cards_container.count() - 1
            self._cards_container.insertWidget(idx, card)
            self._point_cards.append(card)
            if (
                self._selected_point
                and pt.number == self._selected_point.number
            ):
                card.set_selected(True)

    def _on_card_clicked(
        self,
        point: ControlPoint,
    ) -> None:
        self._selected_point = point
        for card in self._point_cards:
            card.set_selected(
                card.point.number == point.number,
            )
        self._update_props()

    def _on_card_dbl_clicked(
        self, point: ControlPoint,
    ) -> None:
        self._selected_point = point
        self._edit_point()

    def _edit_point_for(self, point: ControlPoint) -> None:
        """Редактировать размер по контекстному меню карточки."""
        self._selected_point = point
        for card in self._point_cards:
            card.set_selected(card.point.number == point.number)
        self._update_props()
        self._edit_point()

    def _delete_point_for(self, point: ControlPoint) -> None:
        """Удалить размер по контекстному меню карточки."""
        self._selected_point = point
        self._delete_point()

    def _show_marker_context_menu(
        self,
        point: ControlPoint,
        global_pos: QPoint,
    ) -> None:
        """Показать контекстное меню по правому клику на маркере на чертеже."""
        menu = QMenu(self)
        act_edit = menu.addAction("Редактировать")
        act_edit.triggered.connect(
            lambda: self._edit_point_for(point),
        )
        act_del = menu.addAction("Удалить")
        act_del.triggered.connect(
            lambda: self._delete_point_for(point),
        )
        menu.exec(global_pos)

    def _update_props(self) -> None:
        pt = self._selected_point
        if pt is None:
            for lbl in self._prop_labels.values():
                lbl.setText("—")
            return
        mapping = {
            "Номер": str(pt.number),
            "Тип": pt.kind,
            "Истинное": pt.true_value,
            "Допуск +": pt.tol_plus,
            "Допуск −": pt.tol_minus,
        }
        for key, val in mapping.items():
            self._prop_labels[key].setText(val)

    def _try_auto_import(self, project) -> None:
        """Автоимпорт DIMENSION при первой загрузке DXF."""
        if project.points:
            return
        entities = self._dxf_view.get_dimensions()
        count = self._service.auto_import_dimensions(
            project.project_id,
            entities,
        )
        if count > 0:
            logger.info(
                "Автоимпорт: %d DIMENSION", count,
            )
            QMessageBox.information(
                self, "Автоимпорт",
                f"Импортировано {count} размеров"
                " из чертежа.\n"
                "Задайте допуски для каждого.",
            )
        else:
            logger.info(
                "DIMENSION не найдены, ручной режим",
            )

    # ── Действия ──

    def _add_point(self) -> None:
        logger.debug("Действие: добавить размер")
        if self._service.current_project() is None:
            QMessageBox.warning(
                self, "Нет проекта",
                "Сначала выберите проект.",
            )
            return
        if self._dxf_view.is_pick_mode:
            return
        if self._loaded_dxf:
            self._add_btn.setEnabled(False)
            self._add_btn.setText("Кликните на чертёж...")
            self._dxf_view.enter_pick_mode(
                self._on_pick,
                on_cancel=self._on_pick_cancel,
            )
        else:
            self._open_point_dialog(0.0, 0.0, None)

    def _on_pick(
        self,
        x: float,
        y: float,
        entity: DxfEntityInfo | None,
    ) -> None:
        self._restore_add_btn()
        logger.debug(
            "Pick: (%.1f, %.1f), entity=%s",
            x, y,
            entity.entity_type if entity else None,
        )
        if entity is not None:
            x, y = entity.center_x, entity.center_y
        self._open_point_dialog(x, y, entity)

    def _on_pick_cancel(self) -> None:
        logger.debug("Pick отменён")
        self._restore_add_btn()

    def _restore_add_btn(self) -> None:
        self._add_btn.setEnabled(True)
        self._add_btn.setText("Добавить размер")

    def _open_point_dialog(
        self,
        x: float,
        y: float,
        entity: DxfEntityInfo | None,
    ) -> None:
        dlg = PointDialog(self, prefill=entity)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name, kind, true_val, tol_plus, tol_minus = (
            dlg.data()
        )
        if not name:
            QMessageBox.warning(
                self, "Пустое название",
                "Укажите название размера.",
            )
            return
        handle = entity.handle if entity else ""
        proj = self._service.current_project()
        if not proj:
            return
        next_num = max((p.number for p in proj.points), default=0) + 1
        self._service.add_point(
            proj.project_id,
            next_num,
            name,
            kind,
            true_val,
            tol_plus,
            tol_minus,
            x=x,
            y=y,
            entity_handle=handle,
        )
        self._refresh_points()

    def _edit_point(self) -> None:
        """Редактировать выбранный размер."""
        if self._selected_point is None:
            QMessageBox.information(
                self, "Не выбрано",
                "Выберите размер для редактирования.",
            )
            return
        dlg = PointDialog(
            self,
            edit_point=self._selected_point,
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name, kind, true_val, tol_plus, tol_minus = (
            dlg.data()
        )
        if not name:
            QMessageBox.warning(
                self, "Пустое название",
                "Укажите название размера.",
            )
            return
        proj = self._service.current_project()
        if not proj:
            return
        pt = self._selected_point
        self._service.update_point(
            proj.project_id,
            pt.number,
            name,
            kind,
            true_val,
            tol_plus,
            tol_minus,
            x=pt.x,
            y=pt.y,
            entity_handle=pt.entity_handle,
            measured_value=pt.measured_value,
        )
        self._refresh_points()

    def _delete_point(self) -> None:
        logger.debug("Действие: удалить размер")
        if self._selected_point is None:
            QMessageBox.information(
                self, "Не выбрано",
                "Выберите размер для удаления.",
            )
            return
        proj = self._service.current_project()
        if not proj:
            return
        self._service.remove_point(
            proj.project_id,
            self._selected_point.number,
        )
        self._selected_point = None
        self._refresh_points()

    def _renumber_points(self) -> None:
        """Перенумеровать все контрольные точки."""
        project = self._service.current_project()
        if not project or not project.points:
            return
        for i, pt in enumerate(project.points, start=1):
            pt.number = i
        self._refresh_points()
