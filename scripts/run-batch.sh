#!/usr/bin/env bash
set -euo pipefail

COUNT="${COUNT:-1000}"
INTERVAL="${INTERVAL:-0.005}"
HISTORY_TIMEOUT="${HISTORY_TIMEOUT:-5}"
TRIALS="${TRIALS:-3}"
LOSS_LIST="${LOSS_LIST:-0 1 5 10 20}"

echo "COUNT=$COUNT"
echo "INTERVAL=$INTERVAL"
echo "HISTORY_TIMEOUT=$HISTORY_TIMEOUT"
echo "TRIALS=$TRIALS"
echo "LOSS_LIST=$LOSS_LIST"

for loss in $LOSS_LIST; do
  for trial in $(seq 1 "$TRIALS"); do
    echo "=== single loss=${loss}% trial=${trial} ==="
    scripts/run-experiment.sh \
      single \
      "$loss" \
      0 \
      "$COUNT" \
      "$INTERVAL" \
      "$HISTORY_TIMEOUT" \
      "single_loss${loss}_trial${trial}"

    echo "=== dual loss=${loss}% trial=${trial} ==="
    scripts/run-experiment.sh \
      dual \
      "$loss" \
      "$loss" \
      "$COUNT" \
      "$INTERVAL" \
      "$HISTORY_TIMEOUT" \
      "dual_loss${loss}_trial${trial}"
  done
done

scripts/merge-summaries.py results > results/summary_all.csv

echo "summary written to results/summary_all.csv"
