#!/usr/bin/env bash
set -euo pipefail

LOSS1="${1:-0}"
LOSS2="${2:-0}"

LOSS1="${LOSS1%\%}"
LOSS2="${LOSS2%\%}"

set_loss() {
  local node="$1"
  local dev="$2"
  local loss="$3"

  if [ "$loss" = "0" ] || [ "$loss" = "0.0" ]; then
    docker exec "$node" tc qdisc del dev "$dev" root >/dev/null 2>&1 || true
    echo "$node $dev: loss disabled"
  else
    docker exec "$node" tc qdisc replace dev "$dev" root netem loss "${loss}%"
    echo "$node $dev: loss ${loss}%"
  fi
}

set_loss clab-preof-r1 eth2 "$LOSS1"
set_loss clab-preof-r2 eth2 "$LOSS2"

echo "Current qdisc:"
docker exec clab-preof-r1 tc qdisc show dev eth2 || true
docker exec clab-preof-r2 tc qdisc show dev eth2 || true
