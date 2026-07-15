#!/usr/bin/env python3
import socket
import argparse
import time
import struct

parser = argparse.ArgumentParser()
parser.add_argument("--listen", default="0.0.0.0")
parser.add_argument("--in-port", type=int, default=5000)
parser.add_argument("--path1", default="10.0.14.2")
parser.add_argument("--path2", default="10.0.25.2")
parser.add_argument("--out-port", type=int, default=6000)
parser.add_argument("--gap", type=float, default=0.0,
                    help="optional seconds between sending path1 and path2")
args = parser.parse_args()

rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx.bind((args.listen, args.in_port))

tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"PRF listening on {args.listen}:{args.in_port}")
print(f"PRF duplicates to {args.path1}:{args.out_port} and {args.path2}:{args.out_port}")

while True:
    data, addr = rx.recvfrom(65535)
    if len(data) >= 8:
        seq = struct.unpack("!Q", data[:8])[0]
    else:
        seq = -1

    tx.sendto(data, (args.path1, args.out_port))
    if args.gap > 0:
        time.sleep(args.gap)
    tx.sendto(data, (args.path2, args.out_port))

    print(f"PRF replicated seq={seq} from={addr}")
