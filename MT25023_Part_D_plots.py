import matplotlib.pyplot as plt
import numpy as np

# =========================================================
# HARD-CODED DATA (copied from your CSV — NO FILE READING)
# =========================================================

sizes = [64, 512, 4096, 65536]
threads = [1, 2, 4, 8]

# -------------------------
# Throughput (Gbps)
# -------------------------
A1_thr = [0.073583, 0.572926, 4.215354, 24.767470]
A2_thr = [0.071879, 0.584526, 4.173116, 25.665261]
A3_thr = [0.073934, 0.550928, 4.197738, 25.742121]

# -------------------------
# Latency (µs) vs threads (size = 4096)
# -------------------------
A1_lat = [7.748586, 7.793126, 7.674455, 7.757701]
A2_lat = [7.827125, 7.845782, 7.884295, 7.973238]
A3_lat = [7.781283, 7.882016, 7.795700, 7.876166]

# -------------------------
# LLC misses vs message size (threads=1)
# -------------------------
A1_llc = [182348, 153420, 128828, 147530]
A2_llc = [187179, 127657, 152184, 267888]
A3_llc = [158805, 204318, 96192, 118470]

# -------------------------
# Cycles per byte
# cycles / (throughput_bytes)
# using threads=1
# -------------------------
A1_cycles = [9249682073, 9093511338, 10872591278, 9344738486]
A2_cycles = [9153526169, 8939745642, 10283377172, 9533967957]
A3_cycles = [8957101701, 9161911999, 10384352549, 9322236913]

def cycles_per_byte(cycles, thr, size):
    duration = 5  # your experiment duration
    bytes_tx = (thr * 1e9 / 8) * duration
    return cycles / bytes_tx

A1_cpb = [cycles_per_byte(c, t, s) for c, t, s in zip(A1_cycles, A1_thr, sizes)]
A2_cpb = [cycles_per_byte(c, t, s) for c, t, s in zip(A2_cycles, A2_thr, sizes)]
A3_cpb = [cycles_per_byte(c, t, s) for c, t, s in zip(A3_cycles, A3_thr, sizes)]

config = "Intel i7-12700 | TCP | namespaces | 5s duration"

# =========================================================
# PLOT 1: Throughput vs Message Size
# =========================================================
plt.figure()
plt.plot(sizes, A1_thr, marker='o', label="A1 Two-copy")
plt.plot(sizes, A2_thr, marker='o', label="A2 One-copy")
plt.plot(sizes, A3_thr, marker='o', label="A3 Zero-copy")
plt.xscale("log")
plt.xlabel("Message Size (bytes)")
plt.ylabel("Throughput (Gbps)")
plt.title("Throughput vs Message Size\n" + config)
plt.legend()
plt.grid()
plt.savefig("plot_throughput.png")


# =========================================================
# PLOT 2: Latency vs Thread Count
# =========================================================
plt.figure()
plt.plot(threads, A1_lat, marker='o', label="A1 Two-copy")
plt.plot(threads, A2_lat, marker='o', label="A2 One-copy")
plt.plot(threads, A3_lat, marker='o', label="A3 Zero-copy")
plt.xlabel("Thread Count")
plt.ylabel("Latency (µs)")
plt.title("Latency vs Thread Count (size=4096)\n" + config)
plt.legend()
plt.grid()
plt.savefig("plot_latency.png")


# =========================================================
# PLOT 3: LLC Cache Misses vs Message Size
# =========================================================
plt.figure()
plt.plot(sizes, A1_llc, marker='o', label="A1 Two-copy")
plt.plot(sizes, A2_llc, marker='o', label="A2 One-copy")
plt.plot(sizes, A3_llc, marker='o', label="A3 Zero-copy")
plt.xscale("log")
plt.xlabel("Message Size (bytes)")
plt.ylabel("LLC Cache Misses")
plt.title("LLC Misses vs Message Size\n" + config)
plt.legend()
plt.grid()
plt.savefig("plot_cache_misses.png")


# =========================================================
# PLOT 4: CPU Cycles per Byte
# =========================================================
plt.figure()
plt.plot(sizes, A1_cpb, marker='o', label="A1 Two-copy")
plt.plot(sizes, A2_cpb, marker='o', label="A2 One-copy")
plt.plot(sizes, A3_cpb, marker='o', label="A3 Zero-copy")
plt.xscale("log")
plt.xlabel("Message Size (bytes)")
plt.ylabel("Cycles per Byte")
plt.title("CPU Cycles per Byte vs Message Size\n" + config)
plt.legend()
plt.grid()
plt.savefig("plot_cycles_per_byte.png")

plt.show()
