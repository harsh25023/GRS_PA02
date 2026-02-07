#MT25023

CC=gcc
CFLAGS=-O2 -Wall -Wextra -pthread
COMMON=MT25023_Part_B_latency.c

all: server_A1 client_A1 server_A2 client_A2 server_A3 client_A3

server_A1: MT25023_Part_A1_Server.c
	$(CC) $(CFLAGS) $^ -o $@

client_A1: MT25023_Part_A1_Client.c $(COMMON)
	$(CC) $(CFLAGS) $^ -o $@

server_A2: MT25023_Part_A2_Server.c
	$(CC) $(CFLAGS) $^ -o $@

client_A2: MT25023_Part_A2_Client.c $(COMMON)
	$(CC) $(CFLAGS) $^ -o $@

server_A3: MT25023_Part_A3_Server.c
	$(CC) $(CFLAGS) $^ -o $@

client_A3: MT25023_Part_A3_Client.c $(COMMON)
	$(CC) $(CFLAGS) $^ -o $@

clean:
	rm -f server_* client_* results.csv perf.txt out.txt plot.pdf plots.pdf

.PHONY: run_A1 run_A2 run_A3 test exp plot

PORT=9000
SIZE=4096
DUR=5
THREADS=2
IP=127.0.0.1

run_A1: server_A1 client_A1
	./server_A1 $(PORT) $(SIZE) $(THREADS) & pid=$$!; sleep 2; timeout 10 ./client_A1 $(IP) $(PORT) $(DUR) $(SIZE); kill $$pid 2>/dev/null || true; wait $$pid 2>/dev/null || true

run_A2: server_A2 client_A2
	./server_A2 $(PORT) $(SIZE) $(THREADS) & pid=$$!; sleep 2; timeout 10 ./client_A2 $(IP) $(PORT) $(DUR) $(SIZE); kill $$pid 2>/dev/null || true; wait $$pid 2>/dev/null || true

run_A3: server_A3 client_A3
	./server_A3 $(PORT) $(SIZE) $(THREADS) & pid=$$!; sleep 2; timeout 10 ./client_A3 $(IP) $(PORT) $(DUR) $(SIZE); kill $$pid 2>/dev/null || true; wait $$pid 2>/dev/null || true

test: run_A1 run_A2 run_A3

exp:
	bash MT25023_Part_C_run_experiments.sh

plot:
	python3 MT25023_Part_D_plots.py

.PHONY: demo

demo:
	@echo "===== Cleaning ====="
	$(MAKE) clean
	@echo "===== Building ====="
	$(MAKE)
	@echo "===== Quick functionality test (Part A) ====="
	$(MAKE) test
	@echo "===== Running full experiments (Part B + C) ====="
	$(MAKE) exp
	@echo "===== Generating plots (Part D) ====="
	$(MAKE) plot
	@echo "===== Done ====="
	@echo "results.csv and plots.pdf generated"



NS_SERVER=ns_server
NS_CLIENT=ns_client
PORT=9000
SIZE=4096
THREADS=2
DUR=5




.PHONY: ns_setup ns_clean server_A1_ns client_A1_ns run_A1_ns server_A2_ns client_A2_ns run_A2_ns

ns_clean:
	sudo ip netns delete ns_server 2>/dev/null || true
	sudo ip netns delete ns_client 2>/dev/null || true
	sudo ip link delete veth0 2>/dev/null || true

ns_setup:
	sudo ip netns add ns_server
	sudo ip netns add ns_client
	sudo ip link add veth0 type veth peer name veth1
	sudo ip link set veth0 netns ns_server
	sudo ip link set veth1 netns ns_client
	sudo ip netns exec ns_server ip addr add 10.0.0.1/24 dev veth0
	sudo ip netns exec ns_client ip addr add 10.0.0.2/24 dev veth1
	sudo ip netns exec ns_server ip link set lo up
	sudo ip netns exec ns_client ip link set lo up
	sudo ip netns exec ns_server ip link set veth0 up
	sudo ip netns exec ns_client ip link set veth1 up


server_A1_ns: server_A1
	sudo ip netns exec ns_server ./server_A1 9000 4096 3

server_A2_ns: server_A2
	sudo ip netns exec ns_server ./server_A2 9000 4096 3

server_A3_ns: server_A3
	sudo ip netns exec ns_server ./server_A3 9000 4096 2



client_A1_ns: client_A1
	sudo ip netns exec ns_client ./client_A1 10.0.0.1 9000 5 4096

client_A2_ns: client_A2
	sudo ip netns exec ns_client ./client_A2 10.0.0.1 9000 5 4096

client_A3_ns: client_A3
	sudo ip netns exec ns_client ./client_A3 10.0.0.1 9000 5 4096


run_A1_ns: ns_clean ns_setup server_A1 client_A1
	sudo ip netns exec ns_server ./server_A1 9000 4096 3 & \
	pid=$$!; sleep 2; \
	sudo ip netns exec ns_client ./client_A1 10.0.0.1 9000 5 4096; \
	kill $$pid 2>/dev/null || true

run_A2_ns: ns_clean ns_setup server_A2 client_A2
	sudo ip netns exec ns_server ./server_A2 9000 4096 3 & \
	pid=$$!; sleep 2; \
	sudo ip netns exec ns_client ./client_A2 10.0.0.1 9000 5 4096; \
	kill $$pid 2>/dev/null || true

run_A3_ns: ns_clean ns_setup server_A3 client_A3
	sudo ip netns exec ns_server ./server_A3 9000 4096 2 & \
	pid=$$!; sleep 2; \
	sudo ip netns exec ns_client ./client_A3 10.0.0.1 9000 5 4096; \
	kill $$pid 2>/dev/null || true



PERF_EVENTS = cycles,cpu_core/L1-dcache-load-misses/,cpu_core/cache-misses/,context-switches

.PHONY: perf_A1 perf_A2 perf_A3

perf_A1: client_A1
	sudo ip netns exec ns_client \
	perf stat -e $(PERF_EVENTS) \
	./client_A1 10.0.0.1 $(PORT) $(DUR) $(SIZE)

perf_A2: client_A2
	sudo ip netns exec ns_client \
	perf stat -e $(PERF_EVENTS) \
	./client_A2 10.0.0.1 $(PORT) $(DUR) $(SIZE)

perf_A3: client_A3
	sudo ip netns exec ns_client \
	perf stat -e $(PERF_EVENTS) \
	./client_A3 10.0.0.1 $(PORT) $(DUR) $(SIZE)
