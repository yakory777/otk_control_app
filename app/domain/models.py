from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ControlPoint:
    number: int
    name: str
    kind: str
    true_value: str
    tol_plus: str
    tol_minus: str
    x: str = "0.000"
    y: str = "0.000"


@dataclass
class Project:
    project_id: int
    name: str
    dxf_file: str
    description: str
    last_control: str
    points: list[ControlPoint] = field(default_factory=list)
