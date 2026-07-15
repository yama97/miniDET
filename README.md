# miniDET

**miniDET** is a lightweight experimental implementation of a subset of the
Deterministic Networking (DetNet) Packet Replication, Elimination, and Ordering
Functions (PREOF) for commodity IP networks.

This repository contains the source code and containerlab-based experimental
environment used in the following paper:

> **miniDET: A Lightweight Experimental Implementation of a DetNet PREOF Subset for Commodity IP Networks**

miniDET is intended for education, experimentation, and reproducible research.
Rather than implementing the complete DetNet architecture, it provides a minimal
PREOF subset that focuses on packet replication and duplicate elimination.

---

# Features

- User-space Python implementation
- Packet Replication Function (PRF)
- Packet Elimination Function (PEF)
- Containerlab-based experimental topology
- Reproducible evaluation scripts
- Sample experimental results

---

# Repository Structure

```
.
├── Dockerfile                 Docker image definition
├── preof.clab.yml             Containerlab topology
├── sender-flow.py             Packet sender
├── receiver-flow.py           Packet receiver
├── prf.py                     Packet Replication Function
├── pef-history.py             Packet Elimination Function
├── scripts/                   Experiment scripts
└── results/                   Example experimental results
```

---

# Requirements

The experiments were developed and tested with:

- Ubuntu 24.04 LTS
- Docker Engine 29.x
- containerlab 0.75
- Python 3.12

See `results/env/environment.txt` for the complete software environment.

---

# Quick Start

Build the Docker image:

```bash
docker build -t detnet-preof-lab:ubuntu24 .
```

Deploy the topology:

```bash
sudo containerlab deploy -t preof.clab.yml
```

Run the experiments:

```bash
./scripts/run-batch.sh
```

Analyze the results:

```bash
./scripts/analyze-run.py
```

Remove the topology:

```bash
sudo containerlab destroy -t preof.clab.yml
```

---

# Experimental Results

The `results/` directory contains example outputs used in the paper, including:

- packet delivery rate
- residual packet loss
- duplicate packet statistics
- generated figures
- summary CSV files

---

# Reproducibility

This repository contains the complete artifact used to generate the results
reported in the accompanying paper, including:

- source code
- containerlab topology
- Docker environment
- experiment scripts
- plotting scripts
- representative experimental results

---

# License

BSD 3-Clause License.

---

# Citation

If you use miniDET in your research, please cite the accompanying paper.

```bibtex
(To be added after publication.)
```
