from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView


class DxfMockView(QGraphicsView):
    """Заглушка DXF-просмотрщика с демо-контуром."""

    def __init__(self) -> None:
        scene = QGraphicsScene()
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setSceneRect(0, 0, 820, 420)
        self._draw()

    def _draw(self) -> None:
        scene = self.scene()
        pen = QPen(QColor("#475569"))
        pen.setWidthF(2)
        helper = QPen(QColor("#94a3b8"))
        helper.setStyle(Qt.DashLine)

        scene.addRect(160, 120, 430, 170, pen)
        scene.addEllipse(230, 170, 80, 80, pen)
        scene.addEllipse(490, 185, 50, 50, pen)
        scene.addLine(160, 96, 590, 96, helper)
        scene.addLine(590, 120, 690, 120, helper)
        scene.addLine(590, 310, 690, 310, helper)
        scene.addLine(690, 120, 690, 310, helper)
