#!/usr/bin/env python3
import socket
import argparse
import struct
import time
from collections import OrderedDict

HEADER_FMT = "!QQQ"   # flow_id, run_id, seq
HEADER_LEN = struct.calcsize(HEADER_FMT)

parser = argparse.ArgumentParser()
parser.add_argument("--listen", default="0.0.0.0")
parser.add_argument("--in-port", type=int, default=6000)
parser.add_argument("--dst", default="10.0.6.1")
parser.add_argument("--out-port", type=int, default=7000)
parser.add_argument(
    "--history-timeout",
    type=float,
    default=5.0,
    help="duplicate history timeout in seconds"
)
parser.add_argument(
    "--max-entries",
    type=int,
    default=100000,
    help="maximum number of duplicate history entries"
)
args = parser.parse_args()

rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx.bind((args.listen, args.in_port))

tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

seen = OrderedDict()

print(f"PEF listening on {args.listen}:{args.in_port}")
print(f"PEF forwards unique packets to {args.dst}:{args.out_port}")
print(
    f"PEF key=(flow_id, run_id, seq), "
    f"history_timeout={args.history_timeout}s"
)

def cleanup(now):
    # Remove expired entries from the oldest side.
    while seen:
        _oldest_key, oldest_value = next(iter(seen.items()))
        _first_addr, first_time = oldest_value

        if now - first_time <= args.history_timeout:
            break

        seen.popitem(last=False)

    # Safety cap for memory usage.
    while len(seen) > args.max_entries:
        seen.popitem(last=False)

while True:
    data, addr = rx.recvfrom(65535)
    now = time.time()

    cleanup(now)

    if len(data) < HEADER_LEN:
        print(f"PEF DROP short packet from={addr} len={len(data)}")
        continue

    flow_id, run_id, seq = struct.unpack(HEADER_FMT, data[:HEADER_LEN])
    key = (flow_id, run_id, seq)

    if key in seen:
        first_addr, first_time = seen[key]
        delta_ms = (now - first_time) * 1000.0
        print(
            f"PEF DROP duplicate "
            f"flow_id={flow_id} run_id={run_id} seq={seq} "
            f"from={addr} first_from={first_addr} delta_ms={delta_ms:.3f}"
        )
        continue

    seen[key] = (addr, now)
    tx.sendto(data, (args.dst, args.out_port))

    print(
        f"PEF PASS "
        f"flow_id={flow_id} run_id={run_id} seq={seq} "
        f"from={addr} seen_entries={len(seen)}"
    )
