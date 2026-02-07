#include "MT25023_Part_B_latency.h"

#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>

uint64_t now_ns()
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);

    return (uint64_t)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}

void run_latency_test(int fd, size_t size, int duration)
{
    char *buf = malloc(size);

    uint64_t total = 0;
    uint64_t ops = 0;
    size_t bytes = 0;

    uint64_t start = now_ns();

    while ((now_ns() - start) < (uint64_t)duration * 1000000000ULL)
    {
        uint64_t t1 = now_ns();

        
        send(fd, buf, size, 0);

      
        size_t recvd = 0;
        while (recvd < size) {
            ssize_t r = recv(fd, buf + recvd, size - recvd, 0);
            if (r <= 0) goto done;
            recvd += r;
        }

        uint64_t t2 = now_ns();

        total += (t2 - t1);
        ops++;
        bytes += size;
    }

done:

    double throughput = (bytes * 8.0) / (duration * 1e9);
    double latency_us = (double)total / ops / 1000.0;

    printf("Throughput %.6f\n", throughput);
    printf("Latency %.6f\n", latency_us);

    free(buf);
}
