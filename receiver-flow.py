#!/usr/bin/env python3
import socket
import argparse
import struct
import time

HEADER_FMT = "!QQQ"   # flow_id, run_id, seq
HEADER_LEN = struct.calcsize(HEADER_FMT)

parser = argparse.ArgumentParser()
parser.add_argument("--listen", default="0.0.0.0")
parser.add_argument("--port", type=int, default=7000)
args = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((args.listen, args.port))

last_by_flow_run = {}
count = 0
start = time.time()

print(f"receiver listening on {args.listen}:{args.port}")

while True:
    data, addr = sock.recvfrom(65535)
    now = time.time()

    if len(data) < HEADER_LEN:
        print(f"RECV short packet from={addr} len={len(data)}")
        continue

    flow_id, run_id, seq = struct.unpack(HEADER_FMT, data[:HEADER_LEN])
    flow_key = (flow_id, run_id)

    last = last_by_flow_run.get(flow_key)
    gap = None if last is None else seq - last
    last_by_flow_run[flow_key] = seq

    count += 1
    elapsed = now - start

    print(
        f"RECV flow_id={flow_id} run_id={run_id} seq={seq} "
        f"from={addr} count={count} elapsed={elapsed:.3f}s gap={gap}"
    )
