#!/usr/bin/env bash
set -euo pipefail

docker exec clab-preof-r1 tc qdisc del dev eth2 root >/dev/null 2>&1 || true
docker exec clab-preof-r2 tc qdisc del dev eth2 root >/dev/null 2>&1 || true

echo "qdisc cleared"
docker exec clab-preof-r1 tc qdisc show dev eth2 || true
docker exec clab-preof-r2 tc qdisc show dev eth2 || true
