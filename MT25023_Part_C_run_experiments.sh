#!/bin/bash

set -e

sizes=(64 512 4096 65536)
threads=(1 2 4 8)
impls=(A1 A2 A3)

PORT=9000
DURATION=5

OUT="MT25023_Part_C_results.csv"

NS_SERVER=ns_server
NS_CLIENT=ns_client


echo "Cleaning old state..."

pkill server_A1 2>/dev/null || true
pkill server_A2 2>/dev/null || true
pkill server_A3 2>/dev/null || true

sudo ip netns delete $NS_SERVER 2>/dev/null || true
sudo ip netns delete $NS_CLIENT 2>/dev/null || true
sudo ip link delete veth0 2>/dev/null || true

echo "Building..."
make clean
make

echo "impl,size,threads,throughput(Gbps),latency(us),cycles,l1_misses,llc_misses,cs" > $OUT

for impl in "${impls[@]}"; do
for s in "${sizes[@]}"; do
for t in "${threads[@]}"; do

    echo "Running $impl | size=$s | threads=$t"

    sudo ip netns delete $NS_SERVER 2>/dev/null || true
    sudo ip netns delete $NS_CLIENT 2>/dev/null || true
    sudo ip link delete veth0 2>/dev/null || true

    sudo ip netns add $NS_SERVER
    sudo ip netns add $NS_CLIENT

    sudo ip link add veth0 type veth peer name veth1
    sudo ip link set veth0 netns $NS_SERVER
    sudo ip link set veth1 netns $NS_CLIENT

    sudo ip netns exec $NS_SERVER ip addr add 10.0.0.1/24 dev veth0
    sudo ip netns exec $NS_CLIENT ip addr add 10.0.0.2/24 dev veth1

    sudo ip netns exec $NS_SERVER ip link set lo up
    sudo ip netns exec $NS_CLIENT ip link set lo up
    sudo ip netns exec $NS_SERVER ip link set veth0 up
    sudo ip netns exec $NS_CLIENT ip link set veth1 up

    sudo ip netns exec $NS_SERVER ./server_$impl $PORT $s $t &
    sleep 1

    sudo ip netns exec $NS_CLIENT \
    perf stat -x, \
      -e cycles \
      -e cpu_core/L1-dcache-load-misses/ \
      -e cpu_core/cache-misses/ \
      -e context-switches \
      ./client_$impl 10.0.0.1 $PORT $DURATION $s \
      > out.txt 2> perf.txt

    thr=$(grep Throughput out.txt | awk '{print $2}')
    lat=$(grep Latency out.txt | awk '{print $2}')

    cycles=$(grep cycles perf.txt | head -1 | cut -d',' -f1)
    l1=$(grep L1-dcache-load-misses perf.txt | head -1 | cut -d',' -f1)
    llc=$(grep cache-misses perf.txt | head -1 | cut -d',' -f1)
    cs=$(grep context-switches perf.txt | head -1 | cut -d',' -f1)

    echo "$impl,$s,$t,$thr,$lat,$cycles,$l1,$llc,$cs" >> $OUT

    sudo ip netns delete $NS_SERVER 2>/dev/null || true
    sudo ip netns delete $NS_CLIENT 2>/dev/null || true
    sudo ip link delete veth0 2>/dev/null || true

done
done
done

echo "Done."
echo "Results saved to $OUT"

python3 MT25023_Part_D_plots.py
