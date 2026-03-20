from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QContextMenuEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from app.domain.models import (
    STATUS_FAIL,
    STATUS_OK,
    STATUS_WARN,
    ControlPoint,
)

_STATUS_STYLES: dict[str, str] = {
    STATUS_OK: (
        "background: #ecfdf5; color: #047857;"
        " border: 1px solid #a7f3d0;"
        " border-radius: 10px;"
        " padding: 2px 8px; font-size: 11px;"
        " font-weight: 600;"
    ),
    STATUS_WARN: (
        "background: #fffbeb; color: #b45309;"
        " border: 1px solid #fde68a;"
        " border-radius: 10px;"
        " padding: 2px 8px; font-size: 11px;"
        " font-weight: 600;"
    ),
    STATUS_FAIL: (
        "background: #fff1f2; color: #be123c;"
        " border: 1px solid #fecdd3;"
        " border-radius: 10px;"
        " padding: 2px 8px; font-size: 11px;"
        " font-weight: 600;"
    ),
}

_DEFAULT_BADGE_STYLE = (
    "background: #f1f5f9; color: #64748b;"
    " border: 1px solid #e2e8f0;"
    " border-radius: 10px;"
    " padding: 2px 8px; font-size: 11px;"
    " font-weight: 600;"
)


class PointCard(QFrame):
    """Карточка одного контрольного размера."""

    def __init__(
        self,
        point: ControlPoint,
        on_click: Callable[[ControlPoint], None],
        on_dbl_click: (
            Callable[[ControlPoint], None] | None
        ) = None,
        on_edit: Callable[[ControlPoint], None] | None = None,
        on_delete: Callable[[ControlPoint], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.point = point
        self._on_click = on_click
        self._on_dbl_click = on_dbl_click
        self._on_edit = on_edit
        self._on_delete = on_delete
        self.setObjectName("pointCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu,
        )
        self.customContextMenuRequested.connect(
            self._show_context_menu,
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(4)

        header = QHBoxLayout()
        title = QLabel(f"№{point.number} · {point.name}")
        title.setStyleSheet(
            "font-weight: 700; font-size: 13px;",
        )
        header.addWidget(title)
        header.addStretch()

        badge = QLabel(point.status)
        badge.setStyleSheet(
            _STATUS_STYLES.get(
                point.status, _DEFAULT_BADGE_STYLE,
            ),
        )
        header.addWidget(badge)
        lay.addLayout(header)

        sub = QLabel(
            f"{point.kind} · Истинное: {point.true_value}",
        )
        sub.setStyleSheet(
            "color: #64748b; font-size: 12px;",
        )
        lay.addWidget(sub)

        tol = QLabel(
            f"Допуск: {point.tol_plus} / {point.tol_minus}",
        )
        tol.setStyleSheet(
            "color: #64748b; font-size: 12px;",
        )
        lay.addWidget(tol)

    def _show_context_menu(self, pos) -> None:
        menu = self._build_context_menu()
        if menu.actions():
            menu.exec(self.mapToGlobal(pos))

    def _build_context_menu(self) -> QMenu:
        menu = QMenu(self)
        if self._on_edit is not None:
            act_edit = menu.addAction("Редактировать")
            act_edit.triggered.connect(
                lambda: self._on_edit(self.point),
            )
        if self._on_delete is not None:
            act_del = menu.addAction("Удалить")
            act_del.triggered.connect(
                lambda: self._on_delete(self.point),
            )
        return menu

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = self._build_context_menu()
        if menu.actions():
            menu.exec(event.globalPos())
            event.accept()
        else:
            super().contextMenuEvent(event)

    def mousePressEvent(self, event) -> None:
        self._on_click(self.point)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if self._on_dbl_click is not None:
            self._on_dbl_click(self.point)
        super().mouseDoubleClickEvent(event)

    def set_selected(self, selected: bool) -> None:
        name = (
            "pointCardSelected" if selected
            else "pointCard"
        )
        self.setObjectName(name)
        self.setStyleSheet(self.styleSheet())
