#!/usr/bin/env python3
import csv
import math
import os
import statistics
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} summary_all.csv [outdir]", file=sys.stderr)
    sys.exit(1)

csv_path = sys.argv[1]
outdir = sys.argv[2] if len(sys.argv) >= 3 else "results/figures"
os.makedirs(outdir, exist_ok=True)

rows = []
with open(csv_path, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

def to_float(row, key, default=0.0):
    try:
        return float(row.get(key, default))
    except Exception:
        return default

def group_metric(metric):
    grouped = defaultdict(list)
    for row in rows:
        mode = row.get("mode", "")
        loss = to_float(row, "loss1_pct")
        value = to_float(row, metric)
        grouped[(mode, loss)].append(value)
    return grouped

def mean_std(values):
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return values[0], 0.0
    return statistics.mean(values), statistics.stdev(values)

def plot_metric(metric, ylabel, title, outfile, value_multiplier=1.0):
    grouped = group_metric(metric)
    modes = sorted(set(mode for mode, _loss in grouped.keys()))
    losses = sorted(set(loss for _mode, loss in grouped.keys()))

    plt.figure(figsize=(6.4, 4.0))

    for mode in modes:
        xs = []
        ys = []
        yerrs = []

        for loss in losses:
            values = grouped.get((mode, loss), [])
            if not values:
                continue
            values = [v * value_multiplier for v in values]
            m, s = mean_std(values)
            xs.append(loss)
            ys.append(m)
            yerrs.append(s)

        if xs:
            plt.errorbar(xs, ys, yerr=yerrs, marker="o", capsize=3, label=mode)

    plt.xlabel("Configured random loss per path (%)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()

    path = os.path.join(outdir, outfile)
    plt.savefig(path)
    plt.close()
    print(path)

plot_metric(
    metric="residual_loss_pct",
    ylabel="Residual loss (%)",
    title="Residual packet loss",
    outfile="residual_loss_pct.pdf",
    value_multiplier=1.0,
)

plot_metric(
    metric="delivery_rate",
    ylabel="Delivery rate (%)",
    title="Packet delivery rate",
    outfile="delivery_rate_pct.pdf",
    value_multiplier=100.0,
)

plot_metric(
    metric="pef_drop_duplicate_count",
    ylabel="Duplicate drops at PEF",
    title="Duplicate packets eliminated at PEF",
    outfile="duplicate_drops.pdf",
    value_multiplier=1.0,
)

plot_metric(
    metric="pef_max_seen_entries",
    ylabel="Maximum PEF history entries",
    title="Maximum PEF history size",
    outfile="pef_max_seen_entries.pdf",
    value_multiplier=1.0,
)
