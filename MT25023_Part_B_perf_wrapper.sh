#!/bin/bash

perf stat -x, \
-e cycles \
-e L1-dcache-load-misses \
-e LLC-load-misses \
-e context-switches \
"$@" 2> perf.txt
