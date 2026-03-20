from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

STATUS_OK = "Норма"
STATUS_WARN = "Внимание"
STATUS_FAIL = "Брак"
STATUS_NONE = "—"

_WARN_THRESHOLD = 0.8


@dataclass
class ControlPoint:
    number: int
    name: str
    kind: str
    true_value: str
    tol_plus: str
    tol_minus: str
    x: float = 0.0
    y: float = 0.0
    entity_handle: str = ""
    measured_value: str = ""

    @property
    def deviation(self) -> float | None:
        """Отклонение measured - true, None если нет замера."""
        if not self.measured_value:
            return None
        try:
            return (
                float(self.measured_value)
                - float(self.true_value)
            )
        except ValueError:
            return None

    @property
    def status(self) -> str:
        """Норма / Внимание / Брак / —."""
        dev = self.deviation
        if dev is None:
            return STATUS_NONE
        try:
            plus = float(self.tol_plus)
            minus = float(self.tol_minus)
        except ValueError:
            return STATUS_NONE
        if minus <= dev <= plus:
            band = plus - minus
            if band > 0:
                edge = max(
                    abs(dev - minus), abs(dev - plus),
                )
                ratio = 1.0 - edge / band
                if ratio >= _WARN_THRESHOLD:
                    return STATUS_WARN
            return STATUS_OK
        return STATUS_FAIL


@dataclass
class Project:
    project_id: int
    name: str
    dxf_file: str
    description: str
    last_control: str
    points: list[ControlPoint] = field(
        default_factory=list,
    )


@dataclass
class HistoryEntry:
    """Запись в истории изменений по проекту."""
    timestamp: str
    operator: str
    action: str
    point_number: int | None
    old_value: str
    new_value: str
    entry_id: int | None = None
    project_id: int | None = None


@dataclass
class AppConfig:
    """Конфигурация приложения (настройки)."""
    data_dir: str = "data"
    operator: str = ""
    theme: str = "light"
    db_path: str = "data/otk.db"
