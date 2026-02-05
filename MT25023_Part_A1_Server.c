#include "MT25023_Part_A_common.h"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <sys/socket.h>

typedef struct {
    int fd;
    size_t size;
} args_t;


/* -----------------------------
   thread control (runtime limit)
   ----------------------------- */
static int active_threads = 0;
static int max_threads = 0;
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;


/* -----------------------------
   safe recv (full message)
   ----------------------------- */
static int recv_all(int fd, char *buf, size_t n)
{
    size_t rcv = 0;

    while (rcv < n)
    {
        ssize_t r = recv(fd, buf + rcv, n - rcv, 0);
        if (r <= 0) return -1;
        rcv += r;
    }

    return 0;
}


/* -----------------------------
   safe send (full message)
   ----------------------------- */
static int send_all(int fd, char *buf, size_t n)
{
    size_t sent = 0;

    while (sent < n)
    {
        ssize_t s = send(fd, buf + sent, n - sent, 0);
        if (s <= 0) return -1;
        sent += s;
    }

    return 0;
}


/* -----------------------------
   per-client thread
   ----------------------------- */
void *handler(void *arg)
{
    args_t *a = arg;

    int fd = a->fd;
    size_t size = a->size;

    /* REQUIRED: structure with 8 heap fields */
    message_t msg;
    msg_init(&msg, size);

    char *buf = malloc(size);

    while (1)
    {
        /* request */
        if (recv_all(fd, buf, size) < 0)
            break;

        /* prepare reply using structured fields */
        size_t off = 0;

        for (int i = 0; i < FIELDS; i++)
        {
            memcpy(buf + off, msg.field[i], msg.field_size);
            off += msg.field_size;
        }

        /* response */
        if (send_all(fd, buf, size) < 0)
            break;
    }

    close(fd);

    msg_free(&msg);
    free(buf);
    free(a);

    pthread_mutex_lock(&lock);
    active_threads--;
    pthread_mutex_unlock(&lock);

    return NULL;
}


/* -----------------------------
   main server
   ----------------------------- */
int main(int argc, char **argv)
{
    if (argc < 4)
    {
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

    bind(sfd, (void *)&addr, sizeof(addr));
    listen(sfd, 128);

    printf("[A1] Server listening on port %d | msg=%zu | max_threads=%d\n",
           port, size, max_threads);

    while (1)
    {
        int cfd = accept(sfd, NULL, NULL);

        pthread_mutex_lock(&lock);

        if (active_threads >= max_threads)
        {
            close(cfd);  // enforce thread cap
            pthread_mutex_unlock(&lock);
            continue;
        }

        active_threads++;
        pthread_mutex_unlock(&lock);

        printf("[A1] Client connected (active=%d)\n", active_threads);

        args_t *a = malloc(sizeof(args_t));
        a->fd = cfd;
        a->size = size;

        pthread_t t;
        pthread_create(&t, NULL, handler, a);
        pthread_detach(t);
    }
}
