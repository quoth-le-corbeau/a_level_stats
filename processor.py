import math
from typing import List

from models import CentralTendency


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
