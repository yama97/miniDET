#!/usr/bin/env python3
import socket
import struct
import time
import argparse
import random

HEADER_FMT = "!QQQ"   # flow_id, run_id, seq
HEADER_LEN = struct.calcsize(HEADER_FMT)

parser = argparse.ArgumentParser()
parser.add_argument("--dst", default="10.0.1.254")
parser.add_argument("--port", type=int, default=5000)
parser.add_argument("--count", type=int, default=100)
parser.add_argument("--interval", type=float, default=0.05)
parser.add_argument("--flow-id", type=int, default=1)
parser.add_argument("--run-id", type=int, default=None)
args = parser.parse_args()

if args.run_id is None:
    args.run_id = random.getrandbits(64)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"SENDER dst={args.dst}:{args.port}")
print(f"SENDER flow_id={args.flow_id} run_id={args.run_id}")

for seq in range(args.count):
    header = struct.pack(HEADER_FMT, args.flow_id, args.run_id, seq)
    payload = header + f" flow={args.flow_id} run={args.run_id} seq={seq}".encode()

    sock.sendto(payload, (args.dst, args.port))
    print(f"SEND flow_id={args.flow_id} run_id={args.run_id} seq={seq}")

    time.sleep(args.interval)
