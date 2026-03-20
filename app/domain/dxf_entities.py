from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DxfEntityInfo:
    """Данные о геометрической сущности из DXF-чертежа.

    def_x1/y1 и def_x2/y2 -- опциональные точки замера
    (для DIMENSION: defpoint2/defpoint3;
     для LINE: start/end; для CIRCLE/ARC: None).
    """

    handle: str
    entity_type: str
    kind: str
    center_x: float
    center_y: float
    value: str
    label: str
    def_x1: float | None = None
    def_y1: float | None = None
    def_x2: float | None = None
    def_y2: float | None = None
    layer: str = ""
