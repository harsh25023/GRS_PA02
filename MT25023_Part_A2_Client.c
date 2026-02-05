#include "MT25023_Part_B_latency.h"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

int main(int argc, char **argv)
{
    if (argc < 5) {
        printf("Usage: %s <ip> <port> <duration> <size>\n", argv[0]);
        return 1;
    }

    char *ip = argv[1];
    int port = atoi(argv[2]);
    int duration = atoi(argv[3]);
    size_t size = atol(argv[4]);

    int fd = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, ip, &addr.sin_addr);

    connect(fd, (void*)&addr, sizeof(addr));

    printf("[A2] Connected to server\n");

    run_latency_test(fd, size, duration);

    close(fd);
}
