from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CentralTendency:
    mean: float
    median: float
    range: float
    mode: Optional[float]


@dataclass(frozen=True)
class Spread:
    mean: float
    sd: float
