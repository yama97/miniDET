# miniDET

**miniDET** is a lightweight experimental implementation of a subset of the
Deterministic Networking (DetNet) Packet Replication, Elimination, and Ordering
Functions (PREOF) for commodity IP networks.

This repository accompanies the paper:

> **miniDET: A Lightweight Experimental Implementation of a DetNet PREOF Subset for Commodity IP Networks**

miniDET is intended for education, experimentation, and reproducible research.
Rather than implementing the complete DetNet architecture, it provides a
minimal PREOF subset that focuses on packet replication and duplicate
elimination.

---

# Features

- User-space Python implementation
- Packet Replication Function (PRF)
- Packet Elimination Function (PEF)
- Containerlab-based experimental topology
- Reproducible experiment scripts
- Example experimental results

---

# Repository Structure

```
.
├── Dockerfile
├── preof.clab.yml
├── sender-flow.py
├── receiver-flow.py
├── prf.py
├── prf-onepath.py
├── pef-history.py
├── scripts/
├── results/
├── fig-minidet-topology.pdf
├── LICENSE
└── README.md
```

---

# Requirements

The experiments were tested with:

- Ubuntu 24.04 LTS
- Docker Engine 29.x
- containerlab 0.77 or later
- Python 3.12

The following software must be installed before running the experiments:

- Docker Engine
- containerlab

Installation instructions are available from the official websites:

- Docker: https://docs.docker.com/engine/install/
- containerlab: https://containerlab.dev/install/

---

# Quick Start

Clone the repository.

```bash
git clone https://github.com/yama97/miniDET.git
cd miniDET
```

Build the Docker image.

```bash
sudo docker build -t detnet-preof-lab:ubuntu24 .
```

Deploy the containerlab topology.

```bash
sudo containerlab deploy -t preof.clab.yml
```

Verify that all containers are running.

```bash
sudo docker ps
```

You should see the following six containers.

```
clab-preof-h1
clab-preof-prf
clab-preof-r1
clab-preof-r2
clab-preof-pef
clab-preof-h2
```

Run the experiments.

```bash
sudo ./scripts/run-batch.sh
```

Analyze an individual experiment.

```bash
python3 ./scripts/analyze-run.py \
results/<experiment-directory>
```

Remove the topology.

```bash
sudo containerlab destroy -t preof.clab.yml --cleanup
```

---

# Experimental Results

Example experiment results are included in the `results/` directory.

The analysis scripts generate:

- packet delivery rate
- residual packet loss
- duplicate packet statistics
- CSV summaries
- publication-quality figures

---

# Notes

The Python programs (`sender-flow.py`, `prf.py`,
`prf-onepath.py`, `pef-history.py`, and
`receiver-flow.py`) are mounted into the appropriate
containers by `preof.clab.yml`.

No manual `docker cp` operations are required.

---

# Reproducibility

This repository contains the complete artifact used in the
paper, including

- source code
- Docker environment
- containerlab topology
- experiment scripts
- analysis scripts
- representative experiment results

---

# License

BSD 3-Clause License.

---

# Citation

If you use miniDET in your research, please cite the accompanying paper.

(Bibliographic information will be added after publication.)
