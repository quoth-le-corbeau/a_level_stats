from result import Result, Ok, Err
from scipy.stats import norm  # type: ignore
import numpy as np
import math
from typing import List, Tuple, Dict, Callable

import models
from models import CentralTendency, Spread


def p_x_up_to_value(params: models.NormalParams) -> Result[float, str]:
    try:
        return Ok(norm(loc=params.mu, scale=params.sigma).cdf(params.x1))
    except ValueError:
        return Err("Oh dear. An unexpected error occurred.")


def p_x_above_value(params: models.NormalParams) -> Result[float, str]:
    try:
        return Ok(1 - norm(loc=params.mu, scale=params.sigma).cdf(params.x1))
    except ValueError:
        return Err("Oh dear. An unexpected error occurred.")


def p_x_between_values(params: models.NormalParams) -> Result[float, str]:
    try:
        p1 = norm(loc=params.mu, scale=params.sigma).cdf(params.x1)
        p2 = norm(loc=params.mu, scale=params.sigma).cdf(params.x2)
        return Ok(p2 - p1)
    except ValueError:
        return Err("Oh dear. An unexpected error occurred.")


def p_x_outside_values(params: models.NormalParams) -> Result[float, str]:
    try:
        p1 = norm(loc=params.mu, scale=params.sigma).cdf(params.x1)
        p2 = norm(loc=params.mu, scale=params.sigma).cdf(params.x2)
        return Ok(1 - p2 + p1)
    except ValueError:
        return Err("Oh dear. An unexpected error occurred.")


def up_to_value_given_p(params: models.NormalParams) -> Result[float, str]:
    try:
        return Ok(norm.ppf(params.p, loc=params.mu, scale=params.sigma))
    except ValueError:
        return Err("Oh dear. An unexpected error occurred.")


def above_value_given_p(params: models.NormalParams) -> Result[float, str]:
    if params.p is None:
        return Err("Oh dear. An unexpected error occurred.")
    try:
        return Ok(norm.ppf(1 - params.p, loc=params.mu, scale=params.sigma))
    except ValueError:
        return Err("Oh dear. An unexpected error occurred.")


NORMAL_FUNCTIONS: Dict[str, Callable[[models.NormalParams], Result[float, str]]] = {
    "cdf_left": p_x_up_to_value,
    "cdf_right": p_x_above_value,
    "cdf_middle": p_x_between_values,
    "cdf_outside": p_x_outside_values,
    "ppf_left": up_to_value_given_p,
    "ppf_right": above_value_given_p,
}


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
    freq = 1
    point = sorted_data[0]
    for num in sorted_data:
        freq = sorted_data.count(num)
        if freq > counter:
            counter = freq
            point = num
    if freq == 1:
        mode_str: str = ""
        return CentralTendency(mean=mean, median=median, mode=mode_str, range=rng)
    else:
        mode: float = round(number=point, ndigits=dp)
        return CentralTendency(mean=mean, median=median, mode=mode, range=rng)


def get_spread(data_list: List[float], dp: int) -> Spread:
    sorted_data = sorted(data_list)
    sum_n: float = sum(sorted_data)
    n: int = len(sorted_data)
    mean = round(number=sum_n / n, ndigits=dp)
    sd = round(float(np.std(data_list)), dp)
    q1 = sorted_data[math.ceil(n / 4) - 1]
    q3 = sorted_data[math.ceil((3 * n + 1) / 4) - 1]
    return Spread(mean=mean, sd=sd, q1=q1, q3=q3)


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
