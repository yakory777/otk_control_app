from __future__ import annotations

import logging

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.pyqt import PyQtBackend
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QWheelEvent
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QWidget

from app.ui.utils import resource_path

logger = logging.getLogger(__name__)


class DxfView(QGraphicsView):
    """DXF-просмотрщик на базе ezdxf + PyQtBackend.

    Управление:
    - колесо мыши — масштаб (zoom к курсору);
    - Ctrl + колесо — более мелкий шаг;
    - ЛКМ + перетаскивание — панорамирование.
    """

    _ZOOM_IN = 1.15
    _ZOOM_OUT = 1 / 1.15
    _ZOOM_MIN = 0.05
    _ZOOM_MAX = 50.0

    def __init__(self, parent: QWidget | None = None) -> None:
        self._scene = QGraphicsScene()
        super().__init__(self._scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse,
        )
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse,
        )
        self._draw_placeholder()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Масштабирование колесом мыши относительно позиции курсора."""
        delta = event.angleDelta().y()
        factor = self._ZOOM_IN if delta > 0 else self._ZOOM_OUT

        current = self.transform().m11()
        new_scale = current * factor
        if not (self._ZOOM_MIN <= new_scale <= self._ZOOM_MAX):
            return

        self.scale(factor, factor)

    def load_file(self, path: str) -> None:
        """Загрузить и отрисовать DXF-файл по указанному пути.

        Относительные пути разрешаются через resource_path
        (корень проекта / _MEIPASS для PyInstaller-сборки).
        Абсолютные пути (например, из QFileDialog) используются как есть.
        """
        from pathlib import Path

        resolved = (
            path if Path(path).is_absolute()
            else resource_path(path)
        )
        self._scene.clear()
        try:
            doc = ezdxf.readfile(resolved)
        except Exception:
            logger.exception("Ошибка чтения DXF: %s", path)
            self._draw_placeholder()
            return
        try:
            msp = doc.modelspace()
            context = RenderContext(doc)
            backend = PyQtBackend(self._scene)
            frontend = Frontend(context, backend)
            frontend.draw_layout(msp)
            self.fitInView(
                self._scene.sceneRect(),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
        except Exception:
            logger.exception("Ошибка рендеринга DXF: %s", path)
            self._draw_placeholder()

    def _draw_placeholder(self) -> None:
        self._scene.clear()
        self._scene.addText("Файл DXF не загружен")


DxfMockView = DxfView
