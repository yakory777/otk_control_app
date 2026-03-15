from __future__ import annotations

import logging
import math
from collections.abc import Callable
from typing import cast

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.pyqt import PyQtBackend
from PySide6.QtCore import QEvent, QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QContextMenuEvent,
    QBrush,
    QColor,
    QFont,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPen,
    QTransform,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QWidget,
)

from app.domain.dxf_entities import DxfEntityInfo
from app.services.dxf_parser import DxfParser
from app.ui.utils import resource_path

logger = logging.getLogger(__name__)

_MARKER_COLORS = [
    QColor("#10b981"),
    QColor("#0ea5e9"),
    QColor("#f59e0b"),
    QColor("#ef4444"),
    QColor("#8b5cf6"),
    QColor("#ec4899"),
]

_LEADER_ANGLES = [
    40, 140, -40, -140, 20, 160, -20, -160,
    60, 120, -60, -120,
]

_BG_COLOR = QColor(24, 24, 32, 210)


_MOVABLE_FLAGS = (
    QGraphicsItem.GraphicsItemFlag.ItemIsMovable
    | QGraphicsItem.GraphicsItemFlag
    .ItemSendsGeometryChanges
)


class _PanLayerItem(QGraphicsRectItem):
    """Невидимый слой «пустое место»: только приём кликов, панорамирование во view."""

    def __init__(self, rect: QRectF) -> None:
        super().__init__(rect)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.setZValue(10000)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setCursor(Qt.CursorShape.OpenHandCursor)


class _LeaderLink:
    """Связь leader-линии между crosshair и label.

    Обе стороны при перемещении вызывают update_leader(),
    который перерисовывает линию от центра кроссхейра
    до центра лейбла.
    """

    def __init__(
        self, leader: QGraphicsLineItem,
    ) -> None:
        self.leader = leader
        self._crosshair: _CrosshairItem | None = None
        self._label: _CalloutGroup | None = None

    def bind(
        self,
        crosshair: _CrosshairItem,
        label: _CalloutGroup,
    ) -> None:
        self._crosshair = crosshair
        self._label = label
        self.update()

    def update(self) -> None:
        if (
            self._crosshair is None
            or self._label is None
        ):
            return
        cp = self._crosshair.center_point()
        lp = self._label.center_point()
        self.leader.setLine(
            cp.x(), cp.y(), lp.x(), lp.y(),
        )


class _CrosshairItem(QGraphicsRectItem):
    """Подвижный кроссхейр привязки к entity."""

    def __init__(
        self,
        cx: float,
        cy: float,
        arm: float,
        pen: QPen,
    ) -> None:
        super().__init__(
            cx - arm, cy - arm,
            arm * 2, arm * 2,
        )
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.setZValue(10001)
        self.setFlags(_MOVABLE_FLAGS)
        self.setCursor(
            Qt.CursorShape.SizeAllCursor,
        )
        self._link: _LeaderLink | None = None

        h = QGraphicsLineItem(
            cx - arm, cy, cx + arm, cy, self,
        )
        h.setPen(pen)
        v = QGraphicsLineItem(
            cx, cy - arm, cx, cy + arm, self,
        )
        v.setPen(pen)

    def set_link(self, link: _LeaderLink) -> None:
        self._link = link

    def center_point(self) -> QPointF:
        return self.mapToScene(self.rect().center())

    def itemChange(self, change, value):
        if (
            change
            == QGraphicsItem.GraphicsItemChange
            .ItemPositionHasChanged
            and self._link is not None
        ):
            self._link.update()
        return super().itemChange(change, value)


class _CalloutGroup(QGraphicsRectItem):
    """Перетаскиваемый лейбл выноски."""

    def __init__(
        self,
        w: float,
        h: float,
        color: QColor,
        line_w: float,
        parent: QGraphicsItem | None = None,
    ) -> None:
        super().__init__(0, 0, w, h, parent)
        self.setBrush(QBrush(_BG_COLOR))
        self.setPen(QPen(color, line_w))
        self.setZValue(10002)
        self.setFlags(_MOVABLE_FLAGS)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._link: _LeaderLink | None = None

    def set_link(self, link: _LeaderLink) -> None:
        self._link = link

    def center_point(self) -> QPointF:
        return self.mapToScene(self.rect().center())

    def itemChange(self, change, value):
        if (
            change
            == QGraphicsItem.GraphicsItemChange
            .ItemPositionHasChanged
            and self._link is not None
        ):
            self._link.update()
        return super().itemChange(change, value)


class DxfView(QGraphicsView):
    """DXF-просмотрщик с pick mode и маркерами.

    Управление:
    - колесо мыши — масштаб (zoom к курсору);
    - ЛКМ + перетаскивание — панорамирование;
    - pick mode: клик -> выбор ближайшей entity.
    Выноски можно двигать мышью.
    """

    _ZOOM_IN = 1.15
    _ZOOM_OUT = 1 / 1.15
    _ZOOM_MIN = 0.05
    _ZOOM_MAX = 50.0

    def __init__(
        self,
        parser: DxfParser | None = None,
        parent: QWidget | None = None,
    ) -> None:
        self._scene = QGraphicsScene()
        super().__init__(self._scene, parent)
        self._parser = parser or DxfParser()
        self._marker_items: list[QGraphicsItem] = []
        self._entities: list[DxfEntityInfo] = []
        self._doc = None
        self._msp = None
        self._visible_layers: frozenset[str] | None = None
        self._last_points: list = []
        self._pick_mode = False
        self._pick_callback: (
            Callable[
                [float, float, DxfEntityInfo | None],
                None,
            ]
            | None
        ) = None
        self._pick_cancel: (
            Callable[[], None] | None
        ) = None
        self._pick_overlay_item: QGraphicsSimpleTextItem | None = None
        self._pick_highlight_item: QGraphicsRectItem | None = None
        self._pan_start: QPoint | None = None
        self._pan_last_global: QPointF | None = None
        self._pan_scroll_h: int | None = None
        self._pan_scroll_v: int | None = None
        self._pan_scene_anchor: QPointF | None = None
        self._pan_button: Qt.MouseButton | None = None
        self._pan_move_count: int = 0
        self._pan_layer_item: QGraphicsRectItem | None = None
        self._content_rect: QRectF | None = None
        self._on_marker_context_menu: (
            Callable[..., None] | None
        ) = None
        self.setRenderHint(
            QPainter.RenderHint.Antialiasing, True,
        )
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.NoAnchor,
        )
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.NoAnchor,
        )
        self.scale(1, -1)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.viewport().installEventFilter(self)
        self._draw_placeholder()

    def _start_pan(self, ev: QMouseEvent) -> bool:
        """Один способ панорамирования: только ЛКМ по слою «пустое место»."""
        if ev.button() != Qt.MouseButton.LeftButton or self._pick_mode:
            return False
        if self._pan_layer_item is None:
            return False
        scene_pos = self.mapToScene(ev.pos())
        item = self._scene.itemAt(
            scene_pos,
            self.viewportTransform(),
        )
        return item is self._pan_layer_item

    def _log_view_position(self, label: str) -> None:
        """Логировать положение центра вида в координатах сцены (относительно 0,0)."""
        center = self.mapToScene(
            self.viewport().rect().center(),
        )
        logger.debug(
            "%s: центр вида в сцене (относительно 0,0) x=%.2f y=%.2f",
            label,
            center.x(),
            center.y(),
        )

    def eventFilter(self, watched: QWidget, event: QEvent) -> bool:
        """Единственный механизм панорамирования: viewport, координаты ev.pos()."""
        if watched != self.viewport():
            return super().eventFilter(watched, event)
        if event.type() == QEvent.Type.MouseButtonPress:
            ev = cast(QMouseEvent, event)
            btn = ev.button()
            logger.debug(
                "Мышь: нажатие кнопки %s, viewport pos (%d, %d)",
                str(btn).split(".")[-1] if "." in str(btn) else str(btn),
                ev.pos().x(),
                ev.pos().y(),
            )
            if self._start_pan(ev):
                self._pan_start = ev.pos()
                self._pan_last_global = ev.globalPosition()
                self._pan_scroll_h = self.horizontalScrollBar().value()
                self._pan_scroll_v = self.verticalScrollBar().value()
                self._pan_scene_anchor = self.mapToScene(ev.pos())
                self._pan_button = ev.button()
                self._log_view_position("Панорама старт")
                return True
        elif event.type() == QEvent.Type.MouseMove:
            ev = cast(QMouseEvent, event)
            if (
                self._pan_start is not None
                and self._pan_last_global is not None
                and self._pan_scroll_h is not None
                and self._pan_scroll_v is not None
            ):
                total = ev.globalPosition() - self._pan_last_global
                self.horizontalScrollBar().setValue(
                    self._pan_scroll_h - int(total.x()),
                )
                self.verticalScrollBar().setValue(
                    self._pan_scroll_v - int(total.y()),
                )
                self._pan_move_count += 1
                if self._pan_move_count % 10 == 0:
                    self._log_view_position("Панорама движение")
                return True
        elif event.type() == QEvent.Type.MouseButtonRelease:
            ev = cast(QMouseEvent, event)
            btn = ev.button()
            logger.debug(
                "Мышь: отпускание кнопки %s",
                str(btn).split(".")[-1] if "." in str(btn) else str(btn),
            )
            if (
                self._pan_start is not None
                and self._pan_button is not None
                and ev.button() == self._pan_button
            ):
                self._log_view_position("Панорама конец")
                self._pan_start = None
                self._pan_last_global = None
                self._pan_scroll_h = None
                self._pan_scroll_v = None
                self._pan_scene_anchor = None
                self._pan_button = None
                self._pan_move_count = 0
                return True
        return super().eventFilter(watched, event)

    # ── Масштабирование ──

    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y()
        factor = (
            self._ZOOM_IN
            if delta > 0
            else self._ZOOM_OUT
        )
        current = self.transform().m11()
        new_scale = current * factor
        if not (
            self._ZOOM_MIN
            <= new_scale
            <= self._ZOOM_MAX
        ):
            return
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse,
        )
        self.scale(factor, factor)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.NoAnchor,
        )

    # ── Загрузка файла ──

    def load_file(self, path: str) -> None:
        """Загрузить и отрисовать DXF-файл."""
        from pathlib import Path

        resolved = (
            path
            if Path(path).is_absolute()
            else resource_path(path)
        )
        logger.info("Загрузка DXF: %s", resolved)
        self._scene.clear()
        self._entities.clear()
        self._marker_items.clear()
        self._doc = None
        self._msp = None
        self._visible_layers = None
        try:
            doc = ezdxf.readfile(resolved)
        except Exception:
            logger.exception(
                "Ошибка чтения DXF: %s", path,
            )
            self._content_rect = None
            self._draw_placeholder()
            return
        try:
            msp = doc.modelspace()
            self._doc = doc
            self._msp = msp
            context = RenderContext(doc)
            backend = PyQtBackend(self._scene)
            frontend = Frontend(context, backend)
            frontend.draw_layout(
                msp,
                filter_func=self._layer_filter,
            )
            self._set_dxf_items_ignore_mouse()
            self._add_pan_layer()
            content_rect = self._scene.itemsBoundingRect()
            if content_rect.isEmpty() or content_rect.width() < 1 or content_rect.height() < 1:
                content_rect = self._scene.sceneRect()
            if content_rect.isEmpty():
                content_rect = QRectF(-100, -100, 200, 200)
            margin_x = max(content_rect.width() * 0.25, 50.0)
            margin_y = max(content_rect.height() * 0.25, 50.0)
            margin_rect = content_rect.adjusted(
                -margin_x, -margin_y, margin_x, margin_y,
            )
            self._scene.setSceneRect(margin_rect)
            self.fitInView(
                content_rect,
                Qt.AspectRatioMode.KeepAspectRatio,
            )
            self._content_rect = content_rect
            self._entities = self._parser.parse_file(
                resolved,
            )
            logger.info(
                "DXF отрисован, %d entity",
                len(self._entities),
            )
        except Exception:
            logger.exception(
                "Ошибка рендеринга DXF: %s", path,
            )
            self._doc = None
            self._msp = None
            self._content_rect = None
            self._draw_placeholder()

    def _layer_filter(self, entity) -> bool:
        """Фильтр отрисовки по включённым слоям."""
        if self._visible_layers is None:
            return True
        layer = entity.dxf.get("layer", "0")
        return layer in self._visible_layers

    def _set_dxf_items_ignore_mouse(self) -> None:
        """Отключить приём мыши у элементов DXF — клики обрабатывает слой панорамирования."""
        for item in self._scene.items():
            item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def _add_pan_layer(self) -> None:
        """Добавить слой «пустое место» под маркерами; панорамирование только по нему."""
        self._pan_layer_item = None
        r = self._scene.sceneRect()
        if r.isEmpty() or r.width() < 1 or r.height() < 1:
            r = self._scene.itemsBoundingRect()
        if r.isEmpty():
            r = QRectF(-1e6, -1e6, 2e6, 2e6)
        margin = max(r.width(), r.height(), 100) * 0.2
        big = r.adjusted(-margin, -margin, margin, margin)
        pan = _PanLayerItem(big)
        self._scene.addItem(pan)
        self._pan_layer_item = pan

    def get_available_layers(self) -> list[str]:
        """Уникальные имена слоёв из распознанных entity, отсортированные."""
        names = {e.layer for e in self._entities}
        return sorted(names)

    def set_visible_layers(
        self,
        layers: frozenset[str] | None,
    ) -> None:
        """Задать видимые слои; None — все. Перерисовывает DXF и маркеры."""
        if self._visible_layers == layers:
            return
        self._visible_layers = layers
        self._redraw_dxf()

    def _redraw_dxf(self) -> None:
        """Перерисовать DXF по текущему фильтру слоёв и восстановить маркеры.

        Сохраняет текущий масштаб и панораму (transform), чтобы вид не сбрасывался.
        """
        if self._doc is None or self._msp is None:
            return
        saved_transform = self.transform()
        self._pan_layer_item = None
        self._scene.clear()
        self._marker_items.clear()
        context = RenderContext(self._doc)
        backend = PyQtBackend(self._scene)
        frontend = Frontend(context, backend)
        frontend.draw_layout(
            self._msp,
            filter_func=self._layer_filter,
        )
        self._set_dxf_items_ignore_mouse()
        self._add_pan_layer()
        self.setTransform(saved_transform)
        if self._last_points:
            self.set_point_markers(self._last_points)

    # ── Доступ к entity ──

    def get_all_entities(self) -> list[DxfEntityInfo]:
        """Все распознанные геометрические сущности."""
        return list(self._entities)

    def get_dimensions(self) -> list[DxfEntityInfo]:
        """Только DIMENSION-сущности."""
        return [
            e for e in self._entities
            if e.entity_type == "DIMENSION"
        ]

    # ── Pick mode ──

    @property
    def is_pick_mode(self) -> bool:
        return self._pick_mode

    def enter_pick_mode(
        self,
        callback: Callable[
            [float, float, DxfEntityInfo | None],
            None,
        ],
        on_cancel: Callable[[], None] | None = None,
    ) -> None:
        """Войти в режим выбора entity кликом."""
        logger.debug("Вход в pick mode")
        self._pick_mode = True
        self._pick_callback = callback
        self._pick_cancel = on_cancel
        self.setDragMode(
            QGraphicsView.DragMode.NoDrag,
        )
        self.setCursor(Qt.CursorShape.CrossCursor)
        rect = self._scene.sceneRect()
        cx = rect.center().x()
        cy = rect.center().y()
        self._pick_overlay_item = QGraphicsSimpleTextItem(
            "Кликните на размер на чертеже",
        )
        self._pick_overlay_item.setPos(cx - 80, cy - 10)
        self._pick_overlay_item.setZValue(10004)
        self._pick_overlay_item.setTransform(
            QTransform.fromScale(1, -1),
        )
        self._pick_overlay_item.setBrush(
            QBrush(QColor(148, 163, 184)),
        )
        self._scene.addItem(self._pick_overlay_item)
        self._pick_highlight_item = QGraphicsRectItem(-15, -15, 30, 30)
        self._pick_highlight_item.setPen(
            QPen(QColor(14, 165, 233), 2),
        )
        self._pick_highlight_item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self._pick_highlight_item.setZValue(10005)
        self._pick_highlight_item.hide()
        self._scene.addItem(self._pick_highlight_item)

    def _exit_pick_mode(self) -> None:
        logger.debug("Выход из pick mode")
        self._pick_mode = False
        self._pick_callback = None
        self._pick_cancel = None
        if self._pick_overlay_item:
            self._scene.removeItem(self._pick_overlay_item)
            self._pick_overlay_item = None
        if self._pick_highlight_item:
            self._scene.removeItem(self._pick_highlight_item)
            self._pick_highlight_item = None
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.unsetCursor()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._pick_mode and self._pick_highlight_item:
            scene_pt = self.mapToScene(event.pos())
            dxf_x = scene_pt.x()
            dxf_y = scene_pt.y()
            entity = self._parser.find_nearest(
                self._entities,
                dxf_x,
                dxf_y,
                visible_layers=self._visible_layers,
            )
            if entity is not None:
                self._pick_highlight_item.setPos(
                    entity.center_x,
                    entity.center_y,
                )
                self._pick_highlight_item.show()
            else:
                self._pick_highlight_item.hide()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(
        self, event: QMouseEvent,
    ) -> None:
        if not self._pick_mode:
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            scene_pt = self.mapToScene(event.pos())
            dxf_x = scene_pt.x()
            dxf_y = scene_pt.y()
            entity = self._parser.find_nearest(
                self._entities,
                dxf_x,
                dxf_y,
                visible_layers=self._visible_layers,
            )
            cb = self._pick_callback
            self._exit_pick_mode()
            if cb is not None:
                cb(dxf_x, dxf_y, entity)
            return

        if (
            event.button()
            == Qt.MouseButton.RightButton
        ):
            cancel = self._pick_cancel
            self._exit_pick_mode()
            if cancel is not None:
                cancel()
            return

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        if self._pick_mode:
            super().contextMenuEvent(event)
            return
        scene_pos = self.mapToScene(event.pos())
        item = self._scene.itemAt(scene_pos, self.viewportTransform())
        while item is not None:
            pt = item.data(0)
            if pt is not None and self._on_marker_context_menu is not None:
                self._on_marker_context_menu(pt, event.globalPos())
                event.accept()
                return
            item = item.parentItem()
        super().contextMenuEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if (
            self._pick_mode
            and event.key() == Qt.Key.Key_Escape
        ):
            cancel = self._pick_cancel
            self._exit_pick_mode()
            if cancel is not None:
                cancel()
            return
        super().keyPressEvent(event)

    # ── Маркеры-выноски ──

    def set_point_markers(
        self,
        points: list,
        on_marker_context_menu: (
            Callable[..., None] | None
        ) = None,
    ) -> None:
        """Перетаскиваемые выноски с размерами.

        on_marker_context_menu(point, global_pos) вызывается при правом клике
        по маркеру на чертеже.
        """
        self._last_points = list(points)
        if on_marker_context_menu is not None:
            self._on_marker_context_menu = on_marker_context_menu
        logger.debug(
            "Обновление маркеров: %d точек",
            len(points),
        )
        for item in self._marker_items:
            self._scene.removeItem(item)
        self._marker_items.clear()

        if not points:
            return

        rect = (
            self._content_rect
            if self._content_rect is not None
            else self._scene.sceneRect()
        )
        ext = max(rect.width(), rect.height(), 1.0)

        dot_r = ext * 0.012
        leader_len = ext * 0.07
        line_w = ext * 0.002
        fsize = max(round(ext * 0.016), 2)
        pad = fsize * 0.5

        font_num = QFont("Segoe UI", fsize)
        font_num.setBold(True)
        font_lbl = QFont(
            "Segoe UI", max(round(fsize * 0.8), 1),
        )

        nc = len(_MARKER_COLORS)
        na = len(_LEADER_ANGLES)

        for i, pt in enumerate(points):
            color = _MARKER_COLORS[i % nc]
            sx, sy = pt.x, pt.y
            ang = math.radians(
                _LEADER_ANGLES[i % na],
            )
            self._add_callout(
                sx, sy, pt, color, ang,
                leader_len, dot_r, line_w,
                font_num, font_lbl, pad,
            )

    def _add_callout(
        self,
        sx: float,
        sy: float,
        pt,
        color: QColor,
        angle: float,
        leader_len: float,
        dot_r: float,
        line_w: float,
        font_num: QFont,
        font_lbl: QFont,
        pad: float,
    ) -> None:
        ch_pen = QPen(color, line_w * 2)
        crosshair = _CrosshairItem(
            sx, sy, dot_r, ch_pen,
        )
        crosshair.setData(0, pt)
        self._scene.addItem(crosshair)
        self._marker_items.append(crosshair)

        num_str = str(pt.number)
        lbl_str = f"  {pt.kind}: {pt.true_value}"

        tmp_num = QGraphicsSimpleTextItem(num_str)
        tmp_num.setFont(font_num)
        nr = tmp_num.boundingRect()

        tmp_lbl = QGraphicsSimpleTextItem(lbl_str)
        tmp_lbl.setFont(font_lbl)
        lr = tmp_lbl.boundingRect()

        box_w = nr.width() + lr.width() + pad * 2
        box_h = max(nr.height(), lr.height()) + pad

        group = _CalloutGroup(
            box_w, box_h, color, line_w,
        )
        group.setData(0, pt)
        flip = QTransform()
        flip.translate(0, box_h)
        flip.scale(1, -1)
        group.setTransform(flip)
        self._scene.addItem(group)
        self._marker_items.append(group)

        num_item = QGraphicsSimpleTextItem(
            num_str, group,
        )
        num_item.setFont(font_num)
        num_item.setBrush(QBrush(color))
        num_item.setPos(pad, pad * 0.5)

        lbl_item = QGraphicsSimpleTextItem(
            lbl_str, group,
        )
        lbl_item.setFont(font_lbl)
        lbl_item.setBrush(
            QBrush(QColor(210, 210, 210)),
        )
        lbl_item.setPos(
            pad + nr.width(),
            pad * 0.5
            + (nr.height() - lr.height()) / 2,
        )

        lx = sx + leader_len * math.cos(angle)
        ly = sy + leader_len * math.sin(angle)
        if math.cos(angle) < 0:
            bx = lx - box_w
        else:
            bx = lx
        by = ly - box_h / 2
        group.setPos(bx, by)

        leader = QGraphicsLineItem()
        leader.setPen(QPen(color, line_w))
        leader.setZValue(10003)
        leader.setData(0, pt)
        self._scene.addItem(leader)
        self._marker_items.append(leader)

        link = _LeaderLink(leader)
        crosshair.set_link(link)
        group.set_link(link)
        link.bind(crosshair, group)

    def clear_markers(self) -> None:
        """Убрать все маркеры со сцены."""
        for item in self._marker_items:
            self._scene.removeItem(item)
        self._marker_items.clear()

    def _draw_placeholder(self) -> None:
        self._doc = None
        self._msp = None
        self._scene.clear()
        item = self._scene.addText(
            "Файл DXF не загружен",
        )
        item.setTransform(QTransform.fromScale(1, -1))
