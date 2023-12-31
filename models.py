from dataclasses import dataclass
from typing import Union, Optional, List


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
    iqr: float
    outliers: List[float]


@dataclass(frozen=True)
class NormalError:
    operation: Optional[str]
    mean: Optional[str]
    standard_deviation: Optional[str]
    x1: Optional[str]
    x2: Optional[str]
    p: Optional[Union[str, float]]
    message: str


@dataclass(frozen=True)
class NormalParams:
    operation: str
    mu: float
    sigma: float
    x1: Optional[float]
    x2: Optional[float]
    p: Optional[float]
