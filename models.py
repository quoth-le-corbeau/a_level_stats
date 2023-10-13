from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class CentralTendency:
    mean: float
    median: float
    range: float
    mode: Union[float, str]


@dataclass(frozen=True)
class Spread:
    mean: float
    sd: float
    q1: float
    q3: float

    @property
    def iqr(self):
        return round((self.q3 - self.q1), 4)
