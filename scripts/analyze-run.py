#!/usr/bin/env python3
import csv
import os
import re
import sys

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} RUN_DIR", file=sys.stderr)
    sys.exit(1)

run_dir = sys.argv[1]

meta = {}
meta_path = os.path.join(run_dir, "meta.env")
if os.path.exists(meta_path):
    with open(meta_path) as f:
        for line in f:
            line = line.strip()
            if not line or "=" not in line:
                continue
            k, v = line.split("=", 1)
            meta[k] = v

sender_log = os.path.join(run_dir, "sender.log")
pef_log = os.path.join(run_dir, "pef-history.log")
receiver_log = os.path.join(run_dir, "receiver-flow.log")

re_sender_info = re.compile(r"SENDER flow_id=(\d+) run_id=(\d+)")
re_send = re.compile(r"SEND flow_id=(\d+) run_id=(\d+) seq=(\d+)")
re_pef_pass = re.compile(
    r"PEF PASS flow_id=(\d+) run_id=(\d+) seq=(\d+) from=\('([^']+)',\s*(\d+)\).*seen_entries=(\d+)"
)
re_pef_drop = re.compile(
    r"PEF DROP duplicate flow_id=(\d+) run_id=(\d+) seq=(\d+) from=\('([^']+)',\s*(\d+)\).*first_from=\('([^']+)',\s*(\d+)\).*delta_ms=([0-9.]+)"
)
re_recv = re.compile(r"RECV flow_id=(\d+) run_id=(\d+) seq=(\d+)")

flow_id = ""
run_id = ""

sent_keys = set()
sent_count = 0

if os.path.exists(sender_log):
    with open(sender_log, errors="replace") as f:
        for line in f:
            m = re_sender_info.search(line)
            if m:
                flow_id, run_id = m.group(1), m.group(2)

            m = re_send.search(line)
            if m:
                fid, rid, seq = m.group(1), m.group(2), int(m.group(3))
                sent_keys.add((fid, rid, seq))
                sent_count += 1
                if not flow_id:
                    flow_id = fid
                if not run_id:
                    run_id = rid

pef_pass_keys = set()
pef_drop_keys = []
pef_pass_count = 0
pef_drop_count = 0
pef_false_drop_count = 0
pef_max_seen_entries = 0
path1_pass_count = 0
path2_pass_count = 0
path1_drop_count = 0
path2_drop_count = 0
delta_ms_values = []

if os.path.exists(pef_log):
    with open(pef_log, errors="replace") as f:
        for line in f:
            m = re_pef_pass.search(line)
            if m:
                fid, rid, seq = m.group(1), m.group(2), int(m.group(3))
                src_ip = m.group(4)
                seen_entries = int(m.group(6))
                key = (fid, rid, seq)

                pef_pass_keys.add(key)
                pef_pass_count += 1
                pef_max_seen_entries = max(pef_max_seen_entries, seen_entries)

                if src_ip == "10.0.12.1":
                    path1_pass_count += 1
                elif src_ip == "10.0.23.1":
                    path2_pass_count += 1

            m = re_pef_drop.search(line)
            if m:
                fid, rid, seq = m.group(1), m.group(2), int(m.group(3))
                src_ip = m.group(4)
                delta_ms = float(m.group(8))
                key = (fid, rid, seq)

                pef_drop_keys.append(key)
                pef_drop_count += 1
                delta_ms_values.append(delta_ms)

                if src_ip == "10.0.12.1":
                    path1_drop_count += 1
                elif src_ip == "10.0.23.1":
                    path2_drop_count += 1

                if key not in pef_pass_keys:
                    pef_false_drop_count += 1

recv_keys = []
recv_key_set = set()

if os.path.exists(receiver_log):
    with open(receiver_log, errors="replace") as f:
        for line in f:
            m = re_recv.search(line)
            if m:
                fid, rid, seq = m.group(1), m.group(2), int(m.group(3))
                key = (fid, rid, seq)
                recv_keys.append(key)
                recv_key_set.add(key)

recv_count_total = len(recv_keys)
recv_count_unique = len(recv_key_set)
receiver_duplicate_leak_count = recv_count_total - recv_count_unique

if sent_count > 0:
    residual_loss_rate = 1.0 - (recv_count_unique / sent_count)
    delivery_rate = recv_count_unique / sent_count
else:
    residual_loss_rate = 0.0
    delivery_rate = 0.0

missing_count = len(sent_keys - recv_key_set)

if delta_ms_values:
    delta_ms_avg = sum(delta_ms_values) / len(delta_ms_values)
    delta_ms_min = min(delta_ms_values)
    delta_ms_max = max(delta_ms_values)
else:
    delta_ms_avg = 0.0
    delta_ms_min = 0.0
    delta_ms_max = 0.0

row = {
    "run_dir": run_dir,
    "timestamp": meta.get("timestamp", ""),
    "tag": meta.get("tag", ""),
    "mode": meta.get("mode", ""),
    "loss1_pct": meta.get("loss1", ""),
    "loss2_pct": meta.get("loss2", ""),
    "configured_count": meta.get("count", ""),
    "interval_sec": meta.get("interval", ""),
    "history_timeout_sec": meta.get("history_timeout", ""),
    "flow_id": flow_id,
    "run_id": run_id,
    "sent_count": sent_count,
    "recv_count_unique": recv_count_unique,
    "recv_count_total": recv_count_total,
    "missing_count": missing_count,
    "delivery_rate": f"{delivery_rate:.6f}",
    "residual_loss_rate": f"{residual_loss_rate:.6f}",
    "residual_loss_pct": f"{residual_loss_rate * 100:.4f}",
    "pef_pass_count": pef_pass_count,
    "pef_drop_duplicate_count": pef_drop_count,
    "pef_false_drop_count": pef_false_drop_count,
    "receiver_duplicate_leak_count": receiver_duplicate_leak_count,
    "pef_max_seen_entries": pef_max_seen_entries,
    "path1_pass_count": path1_pass_count,
    "path2_pass_count": path2_pass_count,
    "path1_drop_count": path1_drop_count,
    "path2_drop_count": path2_drop_count,
    "delta_ms_avg": f"{delta_ms_avg:.6f}",
    "delta_ms_min": f"{delta_ms_min:.6f}",
    "delta_ms_max": f"{delta_ms_max:.6f}",
}

writer = csv.DictWriter(sys.stdout, fieldnames=list(row.keys()))
writer.writeheader()
writer.writerow(row)
