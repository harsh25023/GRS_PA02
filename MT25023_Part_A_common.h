#ifndef PART_A_COMMON_H
#define PART_A_COMMON_H

#include <stdlib.h>
#include <string.h>

#define FIELDS 8


typedef struct {
    char *field[FIELDS];
    size_t field_size;
} message_t;


static inline void msg_init(message_t *m, size_t total_size)
{
    m->field_size = total_size / FIELDS;

    for (int i = 0; i < FIELDS; i++) {
        m->field[i] = (char *)malloc(m->field_size);
        memset(m->field[i], 'A' + i, m->field_size);
    }
}

static inline void msg_free(message_t *m)
{
    for (int i = 0; i < FIELDS; i++)
        free(m->field[i]);
}

#endif
