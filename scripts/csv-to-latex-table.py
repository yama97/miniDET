#!/usr/bin/env python3
import csv
import statistics
import sys
from collections import defaultdict

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} summary_all.csv", file=sys.stderr)
    sys.exit(1)

path = sys.argv[1]

rows = []
with open(path, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

def f(row, key):
    try:
        return float(row[key])
    except Exception:
        return 0.0

groups = defaultdict(list)
for row in rows:
    mode = row.get("mode", "")
    loss = f(row, "loss1_pct")
    groups[(loss, mode)].append(row)

print(r"\begin{table}[t]")
print(r"\centering")
print(r"\caption{Packet delivery results under random loss.}")
print(r"\label{tab:loss-results}")
print(r"\begin{tabular}{c c c c c}")
print(r"\hline")
print(r"Loss (\%) & Mode & Delivery (\%) & Residual loss (\%) & PEF drops \\")
print(r"\hline")

for loss in sorted(set(k[0] for k in groups.keys())):
    for mode in ["single", "dual"]:
        rs = groups.get((loss, mode), [])
        if not rs:
            continue

        delivery = [f(r, "delivery_rate") * 100.0 for r in rs]
        residual = [f(r, "residual_loss_pct") for r in rs]
        drops = [f(r, "pef_drop_duplicate_count") for r in rs]

        d_mean = statistics.mean(delivery)
        r_mean = statistics.mean(residual)
        drop_mean = statistics.mean(drops)

        print(f"{loss:g} & {mode} & {d_mean:.2f} & {r_mean:.2f} & {drop_mean:.1f} \\\\")

print(r"\hline")
print(r"\end{tabular}")
print(r"\end{table}")
