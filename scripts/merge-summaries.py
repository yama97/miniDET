#!/usr/bin/env python3
import csv
import glob
import os
import sys

base = sys.argv[1] if len(sys.argv) >= 2 else "results"

files = sorted(glob.glob(os.path.join(base, "*", "summary.csv")))

if not files:
    print("No summary.csv files found", file=sys.stderr)
    sys.exit(1)

rows = []
fieldnames = None

for path in files:
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if fieldnames is None:
                fieldnames = reader.fieldnames

writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
writer.writeheader()
for row in rows:
    writer.writerow(row)
