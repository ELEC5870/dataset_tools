#!/usr/bin/env python3


from collections import defaultdict
from dataclasses import dataclass
import math
import re

from common import RDEntry, rd_entry, RDParams, Area, LINE_PATTERN


if __name__ == "__main__":
    import argparse
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    import numpy as np
    from tqdm import tqdm

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("input", help="RD dump file")
    args = arg_parser.parse_args()

    rd = defaultdict(list)
    with open(args.input, "r") as f:
        for line in tqdm(f.readlines(), desc="Parsing RD dump"):
            if (entry := rd_entry(line)) is not None:
                rd[entry.params].append(entry.cost)

    @dataclass
    class ParamResults:
        count: int
        mean: float
        sd: float
        cov: float

    param_results = {}
    for params, costs in tqdm(rd.items(), desc="Processing RD dump"):
        mean = sum(costs) / len(costs)
        sd = (sum((cost - mean) ** 2 for cost in costs) / len(costs)) ** 0.5
        cov = sd / mean
        param_results[params] = ParamResults(len(costs), mean, sd, cov)

    multi_results = {k: v for k, v in param_results.items() if v.count > 1 and v.sd > 0}
    highest_cov = max(multi_results.items(), key=lambda r: r[1].cov)

    print(
        "Out of {} unique parameters, {} ({:.2f}%) had multiple results. The average coefficient of variation was {:.2f}%".format(
            len(rd),
            len(multi_results),
            100 * len(multi_results) / len(rd),
            100 * sum(r.cov for r in param_results.values()) / len(param_results),
        )
    )
    print(
        "The highest coefficient of variation was {:.2f}%, for the parameters {}. These results were {}".format(
            100 * highest_cov[1].cov, highest_cov[0], rd[highest_cov[0]]
        )
    )
    print(
        "The unique parameters nearest the origin with multiple results were: {}".format(
            sorted(
                [r for r in multi_results.items()],
                key=lambda r: r[0].area.x + 480 * r[0].area.y,
            )[0]
        )
    )

    min = 1e-4
    data = [max(r.cov, min) for r in param_results.values()]
    plt.hist(
        data,
        bins=np.logspace(np.log10(min), np.log10(max(data)), 250),
        cumulative=True,
        label="Coefficient of Variation",
        weights=np.ones(len(data)) / len(data),
    )
    plt.gca().set_xscale("log")
    plt.gca().xaxis.set_major_formatter(
        PercentFormatter(1, decimals=math.ceil(-(2 + math.log10(min))))
    )
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.show()
