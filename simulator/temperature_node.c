#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { REQUEST_CAPACITY = 64 };

struct temperature_logger {
    bool recording;
    unsigned sample_index;
};

static uint8_t crc8(const char *text)
{
    uint8_t crc = 0;
    for (; *text; ++text) {
        crc ^= (uint8_t)*text;
        for (int bit = 0; bit < 8; ++bit)
            crc = (uint8_t)((crc << 1) ^ ((crc & 0x80) ? 0x07 : 0));
    }
    return crc;
}

static bool decode_request(char *line)
{
    char *separator = strstr(line, " *");
    if (!separator || strlen(separator) != 5 || separator[4] != '\n')
        return false;

    *separator = '\0';
    char expected[3];
    snprintf(expected, sizeof expected, "%02X", (unsigned)crc8(line));
    return memcmp(separator + 2, expected, 2) == 0;
}

static void handle_command(struct temperature_logger *logger, const char *command)
{
    static const unsigned samples[] = {218, 221, 220, 224, 222, 219};
    if (strcmp(command, "BEGIN") == 0) {
        logger->recording = true;
        puts("OK RECORDING");
    } else if (strcmp(command, "END") == 0) {
        logger->recording = false;
        puts("OK IDLE");
    } else if (strcmp(command, "READ") == 0) {
        if (!logger->recording) {
            puts("ERR IDLE");
            return;
        }
        unsigned value = samples[logger->sample_index];
        logger->sample_index = (logger->sample_index + 1)
            % (sizeof samples / sizeof samples[0]);
        printf("OK TEMP %u.%u\n", value / 10, value % 10);
    } else {
        puts("ERR COMMAND");
    }
}

int main(void)
{
    struct temperature_logger logger = {0};
    char line[REQUEST_CAPACITY];
    size_t length = 0;
    bool malformed = false;
    int byte;

    while ((byte = getchar()) != EOF) {
        if (byte == '\n') {
            line[length] = '\n';
            line[length + 1] = '\0';
            if (malformed || !decode_request(line))
                puts("ERR FRAME");
            else
                handle_command(&logger, line);

            if (fflush(stdout) == EOF)
                return 1;
            length = 0;
            malformed = false;
        } else if (byte == '\0' || length == sizeof line - 2) {
            malformed = true;
        } else {
            line[length++] = (char)byte;
        }
    }
    if (length || malformed) {
        puts("ERR FRAME");
        if (fflush(stdout) == EOF)
            return 1;
    }
    return ferror(stdin) ? 1 : 0;
}
