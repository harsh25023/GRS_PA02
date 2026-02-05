#ifndef LATENCY_H
#define LATENCY_H

#include <stdint.h>
#include <stddef.h> 

uint64_t now_ns();
void run_latency_test(int fd, size_t size, int duration);

#endif
