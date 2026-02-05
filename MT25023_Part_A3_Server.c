#include "MT25023_Part_A_common.h"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <string.h>
#include <errno.h>

/*
   A3 — ZERO COPY VERSION
   Uses: sendmsg() + MSG_ZEROCOPY
*/

typedef struct {
    int fd;
    size_t size;
} args_t;

static int active_threads = 0;
static int max_threads = 0;
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;


/* =========================
   recv full message
   ========================= */
static int recv_all(int fd, char *buf, size_t n)
{
    size_t rcv = 0;

    while (rcv < n) {
        ssize_t r = recv(fd, buf + rcv, n - rcv, 0);
        if (r <= 0)
            return -1;
        rcv += r;
    }

    return 0;
}


/* =========================
   Worker thread (one client)
   ========================= */
static void *handler(void *arg)
{
    args_t *a = arg;
    int fd = a->fd;
    size_t size = a->size;

    /* REQUIRED BY ASSIGNMENT:
       8 dynamically allocated heap fields
    */
    message_t msg;
    msg_init(&msg, size);

    char *recvbuf = malloc(size);

    /* scatter/gather iovec */
    struct iovec iov[FIELDS];

    for (int i = 0; i < FIELDS; i++) {
        iov[i].iov_base = msg.field[i];
        iov[i].iov_len  = msg.field_size;
    }

    struct msghdr mh;
    memset(&mh, 0, sizeof(mh));
    mh.msg_iov = iov;
    mh.msg_iovlen = FIELDS;

    /*
       ZERO COPY LOOP
       Kernel pins pages and NIC DMA reads directly
    */
    while (1)
    {
        /* wait for client request */
        if (recv_all(fd, recvbuf, size) < 0)
            break;

        /* ZERO-COPY SEND */
        if (sendmsg(fd, &mh, MSG_ZEROCOPY) < 0) {
            if (errno == EOPNOTSUPP) {
                /* fallback if kernel doesn't support zerocopy */
                sendmsg(fd, &mh, 0);
            } else {
                break;
            }
        }
    }

    close(fd);

    msg_free(&msg);
    free(recvbuf);
    free(a);

    pthread_mutex_lock(&lock);
    active_threads--;
    pthread_mutex_unlock(&lock);

    return NULL;
}


/* =========================
   main
   ========================= */
int main(int argc, char **argv)
{
    if (argc < 4) {
        printf("Usage: %s <port> <size> <threads>\n", argv[0]);
        return 1;
    }

    int port = atoi(argv[1]);
    size_t size = atol(argv[2]);
    max_threads = atoi(argv[3]);

    int sfd = socket(AF_INET, SOCK_STREAM, 0);

    int opt = 1;
    setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = INADDR_ANY;

    bind(sfd, (void*)&addr, sizeof(addr));
    listen(sfd, 128);

    printf("[A3] Server listening on port %d | msg=%zu | max_threads=%d\n",
           port, size, max_threads);

    while (1)
    {
        int cfd = accept(sfd, NULL, NULL);

        pthread_mutex_lock(&lock);

        if (active_threads >= max_threads) {
            close(cfd);
            pthread_mutex_unlock(&lock);
            continue;
        }

        active_threads++;
        pthread_mutex_unlock(&lock);

        printf("[A3] Client connected (active=%d)\n", active_threads);

        args_t *a = malloc(sizeof(args_t));
        a->fd = cfd;
        a->size = size;

        pthread_t t;
        pthread_create(&t, NULL, handler, a);
        pthread_detach(t);
    }
}
