#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-dual}"                  # dual or single
LOSS1="${2:-0}"                    # r1 loss percentage
LOSS2="${3:-0}"                    # r2 loss percentage
COUNT="${4:-1000}"
INTERVAL="${5:-0.005}"
HISTORY_TIMEOUT="${6:-5}"          # PEF duplicate history timeout in seconds
TAG="${7:-test}"

STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="results/${STAMP}_${TAG}_${MODE}_l1-${LOSS1}_l2-${LOSS2}"
mkdir -p "$RUN_DIR"

echo "RUN_DIR=$RUN_DIR"

cat > "$RUN_DIR/meta.env" <<EOF_META
mode=$MODE
loss1=$LOSS1
loss2=$LOSS2
count=$COUNT
interval=$INTERVAL
history_timeout=$HISTORY_TIMEOUT
tag=$TAG
timestamp=$STAMP
EOF_META

echo "[1/8] stopping old processes"
docker exec clab-preof-h2  pkill -f receiver-flow.py >/dev/null 2>&1 || true
docker exec clab-preof-pef pkill -f pef-history.py >/dev/null 2>&1 || true
docker exec clab-preof-prf pkill -f prf.py >/dev/null 2>&1 || true
docker exec clab-preof-prf pkill -f prf-onepath.py >/dev/null 2>&1 || true

sleep 1

echo "[2/8] setting loss"
scripts/set-loss.sh "$LOSS1" "$LOSS2" | tee "$RUN_DIR/qdisc.txt"

echo "[3/8] clearing old container logs"
docker exec clab-preof-h2  rm -f /root/receiver-flow.log
docker exec clab-preof-prf rm -f /root/prf.log

echo "[4/8] starting receiver and PEF with unbuffered Python"
docker exec -d clab-preof-h2  sh -c 'python3 -u /root/receiver-flow.py > /root/receiver-flow.log 2>&1'
docker exec -d clab-preof-pef sh -c "python3 -u /root/pef-history.py --history-timeout ${HISTORY_TIMEOUT} > /root/pef-history.log 2>&1"

# Give receiver and PEF enough time to bind their UDP sockets.
sleep 2

echo "[5/8] starting PRF mode=$MODE with unbuffered Python"
if [ "$MODE" = "single" ]; then
  docker exec -d clab-preof-prf sh -c 'python3 -u /root/prf-onepath.py > /root/prf.log 2>&1'
elif [ "$MODE" = "dual" ]; then
  docker exec -d clab-preof-prf sh -c 'python3 -u /root/prf.py > /root/prf.log 2>&1'
else
  echo "ERROR: MODE must be single or dual" >&2
  exit 1
fi

# Give PRF enough time to bind its UDP socket.
sleep 2

echo "[6/8] running sender"
docker exec -i clab-preof-h1 python3 -u /root/sender-flow.py \
  --count "$COUNT" \
  --interval "$INTERVAL" \
  > "$RUN_DIR/sender.log" 2>&1

# Allow late duplicate packets and all log lines to be written.
sleep 3

echo "[7/8] collecting logs"
docker cp clab-preof-h2:/root/receiver-flow.log "$RUN_DIR/receiver-flow.log" >/dev/null
docker cp clab-preof-pef:/root/pef-history.log "$RUN_DIR/pef-history.log" >/dev/null
docker cp clab-preof-prf:/root/prf.log "$RUN_DIR/prf.log" >/dev/null

echo "[8/8] analyzing"
scripts/analyze-run.py "$RUN_DIR" > "$RUN_DIR/summary.csv"

cat "$RUN_DIR/summary.csv"

echo
echo "Sanity check:"
python3 - <<PYEOF
import csv
from pathlib import Path

summary = Path("$RUN_DIR") / "summary.csv"
with summary.open() as f:
    row = next(csv.DictReader(f))

def get_int(k):
    try:
        return int(float(row.get(k, "0")))
    except Exception:
        return 0

sent = get_int("sent_count")
pef_pass = get_int("pef_pass_count")
recv_unique = get_int("recv_count_unique")
pef_dup = get_int("pef_drop_duplicate_count")
false_drop = get_int("pef_false_drop_count")
rx_dup_leak = get_int("receiver_duplicate_leak_count")
missing = get_int("missing_count")

mode = row.get("mode", "")
loss1 = row.get("loss1_pct", "")
loss2 = row.get("loss2_pct", "")
history_timeout = row.get("history_timeout_sec", "")

print(f"  mode={mode} loss1={loss1}% loss2={loss2}% history_timeout={history_timeout}s")
print(f"  sent_count={sent}")
print(f"  pef_pass_count={pef_pass}")
print(f"  recv_count_unique={recv_unique}")
print(f"  missing_count={missing}")
print(f"  pef_drop_duplicate_count={pef_dup}")
print(f"  pef_false_drop_count={false_drop}")
print(f"  receiver_duplicate_leak_count={rx_dup_leak}")

if loss1 in ("0", "0.0") and loss2 in ("0", "0.0"):
    if recv_unique != sent:
        print("  WARNING: 0% loss test did not deliver all packets.")
        print("           Check pef_pass_count vs recv_count_unique to locate the issue.")
    else:
        print("  OK: 0% loss test delivered all packets.")

if mode == "single" and pef_dup != 0:
    print("  WARNING: single mode should not have duplicate drops.")

if false_drop != 0:
    print("  WARNING: PEF false drops detected.")

if rx_dup_leak != 0:
    print("  WARNING: duplicate packets reached receiver.")
PYEOF

echo
echo "stopping processes"
docker exec clab-preof-h2  pkill -f receiver-flow.py >/dev/null 2>&1 || true
docker exec clab-preof-pef pkill -f pef-history.py >/dev/null 2>&1 || true
docker exec clab-preof-prf pkill -f prf.py >/dev/null 2>&1 || true
docker exec clab-preof-prf pkill -f prf-onepath.py >/dev/null 2>&1 || true

echo "done: $RUN_DIR"
