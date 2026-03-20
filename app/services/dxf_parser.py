from __future__ import annotations

import logging
import math
import re
from collections import Counter
from collections.abc import Iterator

import ezdxf

from app.domain.dxf_entities import DxfEntityInfo

logger = logging.getLogger(__name__)

_DIMTYPE_KIND: dict[int, str] = {
    0: "Линейный",
    1: "Линейный",
    2: "Угол",
    3: "Диаметр",
    4: "Радиус",
    5: "Угол",
    6: "Линейный",
}


class DxfParser:
    """Парсинг DXF-файлов: извлечение entity и поиск."""

    def parse_file(
        self, path: str,
    ) -> list[DxfEntityInfo]:
        """Прочитать DXF и вернуть все распознанные entity.

        Рекурсивно раскрывает INSERT-блоки любой вложенности.
        """
        logger.debug("Парсинг DXF: %s", path)
        doc = ezdxf.readfile(path)
        msp = doc.modelspace()
        result: list[DxfEntityInfo] = []
        counts: Counter[str] = Counter()
        skipped: Counter[str] = Counter()
        for entity in self._iter_entities(msp):
            info = self._parse_entity(entity)
            if info is not None:
                result.append(info)
                counts[info.entity_type] += 1
            else:
                skipped[entity.dxftype()] += 1
        logger.info(
            "DXF распарсен: %d entity из %s (%s)",
            len(result), path,
            ", ".join(
                f"{k}={v}" for k, v in counts.items()
            ) or "пусто",
        )
        if skipped:
            logger.debug(
                "Пропущено: %s",
                ", ".join(
                    f"{k}={v}"
                    for k, v in skipped.items()
                ),
            )
        return result

    def find_nearest(
        self,
        entities: list[DxfEntityInfo],
        x: float,
        y: float,
        max_distance: float | None = None,
        visible_layers: frozenset[str] | None = None,
    ) -> DxfEntityInfo | None:
        """Ближайшая entity в пределах max_distance.

        Если max_distance=None, вычисляется автоматически
        как 10% от размаха координат entity.
        visible_layers: учитывать только entity с этих слоёв;
        None — все слои.
        """
        if not entities:
            return None
        if visible_layers is not None:
            entities = [e for e in entities if e.layer in visible_layers]
            if not entities:
                return None
        if max_distance is None:
            max_distance = self._auto_max_distance(
                entities,
            )
        best: DxfEntityInfo | None = None
        best_dist = float("inf")
        for e in entities:
            d = math.hypot(
                e.center_x - x, e.center_y - y,
            )
            if d < best_dist:
                best_dist = d
                best = e
        if best is not None and best_dist > max_distance:
            logger.debug(
                "Ближайшая entity слишком далеко:"
                " dist=%.1f > max=%.1f",
                best_dist, max_distance,
            )
            return None
        if best is not None:
            logger.debug(
                "Ближайшая entity: %s (%.1f, %.1f)"
                " dist=%.1f",
                best.entity_type, best.center_x,
                best.center_y, best_dist,
            )
        return best

    @staticmethod
    def _auto_max_distance(
        entities: list[DxfEntityInfo],
    ) -> float:
        """10% от диагонали bounding box entity."""
        xs = [e.center_x for e in entities]
        ys = [e.center_y for e in entities]
        span = math.hypot(
            max(xs) - min(xs),
            max(ys) - min(ys),
        )
        return max(span * 0.10, 5.0)

    # ── Рекурсивный обход ──

    @staticmethod
    def _iter_entities(container) -> Iterator:
        """Рекурсивный обход с раскрытием INSERT-блоков."""
        for e in container:
            etype = e.dxftype()
            if etype == "INSERT":
                try:
                    children = list(e.virtual_entities())
                except Exception:
                    logger.debug(
                        "Не удалось раскрыть INSERT %s",
                        e.dxf.get("name", "?"),
                    )
                    continue
                for child in children:
                    if child.dxftype() == "INSERT":
                        yield from (
                            DxfParser._iter_entities(
                                [child],
                            )
                        )
                    else:
                        yield child
            else:
                yield e

    # ── Внутренний парсинг ──

    def _parse_entity(self, e) -> DxfEntityInfo | None:
        etype = e.dxftype()
        if etype == "CIRCLE":
            return self._parse_circle(e)
        if etype == "ARC":
            return self._parse_arc(e)
        if etype == "LINE":
            return self._parse_line(e)
        if etype == "LWPOLYLINE":
            return self._parse_lwpolyline(e)
        if etype == "SPLINE":
            return self._parse_spline(e)
        if etype == "DIMENSION":
            return self._parse_dimension(e)
        return None

    @staticmethod
    def _parse_circle(e) -> DxfEntityInfo:
        cx = float(e.dxf.center.x)
        cy = float(e.dxf.center.y)
        r = float(e.dxf.radius)
        value = f"{2 * r:.3f}"
        layer = e.dxf.get("layer", "0")
        return DxfEntityInfo(
            e.dxf.handle, "CIRCLE", "Диаметр",
            cx, cy, value, f"\u2300{value}",
            layer=layer,
        )

    @staticmethod
    def _parse_arc(e) -> DxfEntityInfo:
        cx = float(e.dxf.center.x)
        cy = float(e.dxf.center.y)
        r = float(e.dxf.radius)
        value = f"{r:.3f}"
        layer = e.dxf.get("layer", "0")
        return DxfEntityInfo(
            e.dxf.handle, "ARC", "Радиус",
            cx, cy, value, f"R{value}",
            layer=layer,
        )

    @staticmethod
    def _parse_line(e) -> DxfEntityInfo:
        x1 = float(e.dxf.start.x)
        y1 = float(e.dxf.start.y)
        x2 = float(e.dxf.end.x)
        y2 = float(e.dxf.end.y)
        length = math.hypot(x2 - x1, y2 - y1)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        value = f"{length:.3f}"
        layer = e.dxf.get("layer", "0")
        return DxfEntityInfo(
            e.dxf.handle, "LINE", "Линейный",
            cx, cy, value, f"L={value}",
            def_x1=x1, def_y1=y1,
            def_x2=x2, def_y2=y2,
            layer=layer,
        )

    @staticmethod
    def _parse_lwpolyline(e) -> DxfEntityInfo | None:
        pts = list(e.get_points(format="xy"))
        if not pts:
            return None
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        perim = 0.0
        for i in range(len(pts) - 1):
            perim += math.hypot(
                pts[i + 1][0] - pts[i][0],
                pts[i + 1][1] - pts[i][1],
            )
        if e.close:
            perim += math.hypot(
                pts[0][0] - pts[-1][0],
                pts[0][1] - pts[-1][1],
            )
        value = f"{perim:.3f}"
        layer = e.dxf.get("layer", "0")
        return DxfEntityInfo(
            e.dxf.handle, "LWPOLYLINE", "Линейный",
            cx, cy, value, f"P={value}",
            layer=layer,
        )

    @staticmethod
    def _parse_spline(e) -> DxfEntityInfo | None:
        pts = list(e.control_points)
        if not pts:
            return None
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        length = 0.0
        try:
            flat = list(e.flattening(0.5))
            for i in range(len(flat) - 1):
                length += math.hypot(
                    flat[i + 1][0] - flat[i][0],
                    flat[i + 1][1] - flat[i][1],
                )
        except Exception:
            pass
        value = f"{length:.3f}"
        layer = e.dxf.get("layer", "0")
        return DxfEntityInfo(
            e.dxf.handle, "SPLINE", "Линейный",
            float(cx), float(cy), value,
            f"S={value}",
            layer=layer,
        )

    def _parse_dimension(
        self, e,
    ) -> DxfEntityInfo:
        dimtype = e.dxf.get("dimtype", 0) & 0x0F
        kind = _DIMTYPE_KIND.get(dimtype, "Другое")
        value = self._extract_dim_value(e)
        pos = self._extract_dim_position(e, dimtype)
        cx = pos.get("cx") or 0.0
        cy = pos.get("cy") or 0.0
        layer = e.dxf.get("layer", "0")
        return DxfEntityInfo(
            e.dxf.handle, "DIMENSION", kind,
            cx, cy,
            value, f"{value} ({kind})",
            def_x1=pos.get("dx1"),
            def_y1=pos.get("dy1"),
            def_x2=pos.get("dx2"),
            def_y2=pos.get("dy2"),
            layer=layer,
        )

    @staticmethod
    def _extract_dim_position(
        entity, dimtype: int,
    ) -> dict[str, float | None]:
        """Вычислить центр и def-точки DIMENSION.

        Линейные (0/1/6): середина defpoint2-defpoint3.
        Радиус/диаметр (3/4): defpoint (на окружности).
        Угол и прочие: text_midpoint как fallback.
        """
        result: dict[str, float | None] = {
            "cx": 0.0, "cy": 0.0,
            "dx1": None, "dy1": None,
            "dx2": None, "dy2": None,
        }
        if dimtype in (0, 1, 6):
            try:
                p2 = entity.dxf.defpoint2
                p3 = entity.dxf.defpoint3
                dx1, dy1 = float(p2.x), float(p2.y)
                dx2, dy2 = float(p3.x), float(p3.y)
                result["cx"] = (dx1 + dx2) / 2
                result["cy"] = (dy1 + dy2) / 2
                result["dx1"] = dx1
                result["dy1"] = dy1
                result["dx2"] = dx2
                result["dy2"] = dy2
                return result
            except (AttributeError, Exception):
                pass
        elif dimtype in (3, 4):
            try:
                dp = entity.dxf.defpoint
                result["cx"] = float(dp.x)
                result["cy"] = float(dp.y)
                return result
            except (AttributeError, Exception):
                pass
        try:
            mid = entity.dxf.text_midpoint
            result["cx"] = float(mid.x)
            result["cy"] = float(mid.y)
        except (AttributeError, Exception):
            try:
                dp = entity.dxf.defpoint
                result["cx"] = float(dp.x)
                result["cy"] = float(dp.y)
            except (AttributeError, Exception):
                pass
        return result

    @staticmethod
    def _extract_dim_value(entity) -> str:
        text = entity.dxf.get("text", "") or ""
        if text and text not in ("<>", " "):
            return text
        try:
            raw = entity.dxf.get("measurement", None)
            if raw is not None:
                return f"{float(raw):.3f}"
        except Exception:
            pass
        return _dim_value_from_mtext(entity)


def _dim_value_from_mtext(entity) -> str:
    """Извлечь значение размера из MTEXT virtual entity."""
    try:
        for ve in entity.virtual_entities():
            if ve.dxftype() == "MTEXT":
                return _clean_mtext(ve.text)
    except Exception:
        pass
    return "?"


_MTEXT_FORMAT_RE = re.compile(
    r"\\[HWQAFfCcTpS][^;]*;",
)
_MTEXT_BRACE_RE = re.compile(r"[{}]")


def _clean_mtext(raw: str) -> str:
    """Убрать formatting-коды MTEXT, оставить значение."""
    result = _MTEXT_FORMAT_RE.sub("", raw)
    result = _MTEXT_BRACE_RE.sub("", result)
    result = result.replace("%%C", "\u2300")
    result = result.replace("%%D", "\u00b0")
    result = result.replace("%%P", "\u00b1")
    return result.strip() or "?"
