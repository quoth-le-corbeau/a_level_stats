import numpy as np
import math
from typing import List, Tuple

from models import CentralTendency, Spread


def get_central_tendency(data_list: List[float], dp: int = 2) -> CentralTendency:
    sorted_data = sorted(data_list)
    sum_n: float = sum(sorted_data)
    n: int = len(sorted_data)
    mean = round(number=sum_n / n, ndigits=dp)
    rng = round(number=sorted_data[-1] - sorted_data[0], ndigits=dp)
    if n % 2 == 0:
        median_lower = sorted_data[int(n / 2) - 1]
        median_upper = sorted_data[int(n / 2)]
        median = (median_upper + median_lower) / 2
    else:
        median = sorted_data[math.floor(n / 2)]
    counter = 0
    point = sorted_data[0]
    for num in sorted_data:
        freq = sorted_data.count(num)
        if freq > counter:
            counter = freq
            point = num
    mode = round(number=point, ndigits=dp)
    return CentralTendency(mean=mean, median=median, mode=mode, range=rng)


def get_spread(data_list: List[float], dp: int = 2) -> Spread:
    sorted_data = sorted(data_list)
    sum_n: float = sum(sorted_data)
    n: int = len(sorted_data)
    mean = round(number=sum_n / n, ndigits=dp)
    np.std(data_list)
    return Spread(mean=mean, sd=3)


def get_bcd(n: int, p: float, x: int, dp: int) -> Tuple[List[str], float]:
    r: int = 0
    cumulative_probability: float = 0.0
    cumulative_array: List[float] = []
    rows: List[str] = []
    p_x: float = 0.0
    while r <= n:
        n_choose_r = math.factorial(n) / (math.factorial(n - r) * math.factorial(r))
        success = p**r
        failure = (1 - p) ** (n - r)
        probability = n_choose_r * success * failure
        cumulative_probability += probability
        cumulative_array.append(round(probability, dp))
        if r == x:
            row = f"==> P(X <= {r}) = {round(cumulative_probability, dp)} <=="
        else:
            row = f"P(X <= {r}) = {round(cumulative_probability, dp)}"
        rows.append(row)
        r += 1
    i = 0
    while i <= x:
        i += 1
        p_x += cumulative_array[i - 1]
    return rows, round(p_x, dp)


def get_bpd(n: int, p: float, x: int, dp: int) -> Tuple[List[str], float]:
    r: int = 0
    # cumulative_probability: float = 0.0
    # cumulative_array: List[float] = []
    rows: List[str] = []
    p_x: float = 0.0
    while r <= n:
        n_choose_r = math.factorial(n) / (math.factorial(n - r) * math.factorial(r))
        success = p**r
        failure = (1 - p) ** (n - r)
        probability = n_choose_r * success * failure
        # cumulative_probability += probability
        # cumulative_array.append(round(probability, dp))
        if r == x:
            row = f"==> P(X = {r}) = {round(probability, dp)} <=="
            p_x = round(probability, dp)
        else:
            row = f"P(X = {r}) = {round(probability, dp)}"
        rows.append(row)
        r += 1
    # i = 0
    # while i <= x:
    #     i += 1
    #     p_x += cumulative_array[i - 1]
    return rows, p_x
