from dataclasses import dataclass


@dataclass(frozen=True)
class CentralTendency:
    mean: float
    median: float
    mode: float
    range: float
