# MT25023 – Programming Assignment 02  
## Multithreaded Socket Systems + Zero-Copy Networking + Performance Analysis

---

## Overview

This assignment implements and evaluates three TCP client–server designs:

| Version | Technique | Copy Model |
|--------|-----------|------------|
| A1 | send()/recv() | Two-copy (baseline) |
| A2 | sendmsg() + iovec | One-copy |
| A3 | sendmsg() + MSG_ZEROCOPY | Zero-copy |

The goal is to study:

- Data movement cost between user ↔ kernel
- Throughput vs latency tradeoffs
- Cache behavior
- CPU overhead
- Effect of thread count
- Effect of message size

All experiments are executed inside **separate Linux network namespaces** as required.

---

# System Used

- CPU: 13th Gen Intel® Core™ i7-13700
- OS: Ubuntu 22.04 LTS (64-bit)
- Compiler: gcc -O2 -pthread
- Profiling: perf stat
- Plotting: matplotlib (Python)

---

# Directory Structure

```
.
├── MT25023_Part_A_common.h
├── MT25023_Part_A1_Server.c
├── MT25023_Part_A1_Client.c
├── MT25023_Part_A2_Server.c
├── MT25023_Part_A2_Client.c
├── MT25023_Part_A3_Server.c
├── MT25023_Part_A3_Client.c
├── MT25023_Part_B_latency.c
├── MT25023_Part_B_latency.h
├── MT25023_Part_C_run_experiments.sh
├── MT25023_Part_D_plots.py
├── Makefile
├── MT25023_Part_C_results.csv
├── MT25023_Assignment_Report.pdf
└── README.md
```

---

# Part A – Implementations

## A1 – Two Copy (Baseline)

- Uses send() / recv()
- Copies:
  1. heap → temp buffer (user memcpy)
  2. temp → kernel socket buffer

## A2 – One Copy

- Uses sendmsg() with iovec
- Eliminates:
  - user memcpy
- Still:
  - kernel copy remains

## A3 – Zero Copy

- Uses sendmsg() + MSG_ZEROCOPY
- Kernel maps pages directly to NIC
- No data copy during send

---

# Build

Compile everything:

```bash
make
```

Clean:

```bash
make clean
```

---

# Running Manually (Localhost)

## A1
```bash
make run_A1
```

## A2
```bash
make run_A2
```

## A3
```bash
make run_A3
```

---

# Running with Separate Namespaces (Required)

## Setup
```bash
make ns_setup
```

## Run server
```bash
make server_A1_ns
```

## Run client (new terminal)
```bash
make client_A1_ns
```

## Cleanup
```bash
make ns_clean
```

---

# Part B – Profiling

Metrics collected:

| Metric | Tool |
|--------|--------|
| Throughput (Gbps) | application |
| Latency (µs) | application |
| CPU cycles | perf |
| Cache misses | perf |
| Context switches | perf |

Manual profiling:

```bash
sudo perf stat \
-e cycles,cache-misses,context-switches \
ip netns exec ns_client ./client_A1 10.0.0.1 9000 5 4096
```

---

# Part C – Automated Experiments

Runs:

- 4 message sizes
- 4 thread counts
- 3 implementations

Total = 48 experiments automatically

## Run all experiments

```bash
bash MT25023_Part_C_run_experiments.sh
```

Generates:

```
MT25023_Part_C_results.csv
```

No manual intervention required.

---

# Part D – Plotting

Plots are generated using **matplotlib**.

Values are **hardcoded** inside the script (as required).

## Generate plots

```bash
python3 MT25023_Part_D_plots.py
```

Generates:

```
throughput_vs_size.png
latency_vs_threads.png
cycles_per_byte.png
L1_vs_size.png
context_switches.png
speedup.png
efficiency.png
...
```

---

# Expected Behavior

## Throughput
Should generally increase:
```
A1 < A2 < A3
```

## Latency
Should generally decrease:
```
A1 > A2 > A3
```

## Cache misses
Should reduce with fewer copies.

## Cycles
Should reduce as copies decrease.

---

# Key Observations

- Zero-copy reduces CPU cycles but may not always improve throughput for small messages
- Larger messages benefit most from zero-copy
- More threads increase cache contention
- Optimal performance occurs near 2–4 threads on this CPU

---

# Running Everything (Full Demo)

```bash
make demo
```

This performs:

1. clean
2. build
3. quick test
4. experiments
5. plots

---

# Submission Checklist

✓ A1 / A2 / A3 code  
✓ Namespace execution  
✓ Automated script  
✓ CSV results  
✓ Matplotlib plots  
✓ Final PDF report  
✓ README  

---


