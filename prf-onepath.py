#!/usr/bin/env python3
import socket
import argparse
import struct

HEADER_FMT = "!QQQ"
HEADER_LEN = struct.calcsize(HEADER_FMT)

parser = argparse.ArgumentParser()
parser.add_argument("--listen", default="0.0.0.0")
parser.add_argument("--in-port", type=int, default=5000)
parser.add_argument("--path1", default="10.0.14.2")
parser.add_argument("--out-port", type=int, default=6000)
args = parser.parse_args()

rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx.bind((args.listen, args.in_port))

tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"PRF-onepath listening on {args.listen}:{args.in_port}")
print(f"PRF-onepath forwards only to {args.path1}:{args.out_port}")

while True:
    data, addr = rx.recvfrom(65535)

    if len(data) >= HEADER_LEN:
        flow_id, run_id, seq = struct.unpack(HEADER_FMT, data[:HEADER_LEN])
    else:
        flow_id, run_id, seq = -1, -1, -1

    tx.sendto(data, (args.path1, args.out_port))

    print(
        f"PRF onepath forwarded "
        f"flow_id={flow_id} run_id={run_id} seq={seq} from={addr}"
    )
