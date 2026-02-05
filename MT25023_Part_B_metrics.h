#pragma once
#include <time.h>

static inline long long now_ns()
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec*1000000000LL + ts.tv_nsec;
}
