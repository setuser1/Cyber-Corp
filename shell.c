#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>

#define BUFF 1024

char* cat(char *filename, char *content, size_t *length) {
    FILE *file = fopen(filename, "r");
    char buffer[BUFF];

    while (fgets(buffer, sizeof(buffer), file)) {
        size_t line = strlen(buffer);
        char *temp = realloc(content, *length + line + 1);
        content = temp;
        strcpy(content + *length, buffer);
        *length += line;
    }

    fclose(file);
    return content;
}

char* touch(char *filename) {
    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        perror("touch");
        return NULL;
    }
    fclose(file);
    return filename;
}

void ls() {
    DIR *dir;
    struct dirent *entry;
    dir = opendir(".");
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] != '.') {
            printf("%s\n", entry->d_name);
        }
    }
    closedir(dir);
}

int main() {
    char *content = malloc(1);
    size_t len = 0;
    content[0] = '\0';

    char input[BUFF];
    while (1) {
        printf("root@localhost:~# ");
        if (!fgets(input, BUFF, stdin)) break;
        input[strcspn(input, "\n")] = '\0';

        if (strncmp(input, "cat ", 4) == 0) {
            char *filename = input + 4;
            while (*filename == ' ') filename++;

            content = cat(filename, content, &len);
            printf("\n--- File Content ---\n%s\n", content);
        } else if (strcmp(input, "exit") == 0) {
            printf("Exiting...\n");
            break;
        } else if (strcmp(input, "ls") == 0) {
            ls();
        } else if (strcmp(input, "clear") == 0) {
            printf("\033[H\033[J");
        } else if (strncmp(input, "cd ", 3) == 0) {
            char *path = input + 3;
            while (*path == ' ') path++;
            if (*path == '\0') {
                fprintf(stderr, "cd: missing operand\n");
            } else if (chdir(path) != 0) {
                perror("cd");
            }
        } else if (strncmp(input, "touch ", 6) == 0) {
            char *filename = input + 6;
            while (*filename == ' ') filename++;
            if (*filename == '\0') {
                fprintf(stderr, "touch: missing operand\n");
            } else {
                if (touch(filename) != NULL) {
                    printf("File '%s' created.\n", filename);
                }
            }
        } else if (strncmp(input, "rm ", 3) == 0) {
            char *filename = input + 3;
            while (*filename == ' ') filename++;
            if (*filename == '\0') {
                fprintf(stderr, "rm: missing operand\n");
            } else {
                if (remove(filename) == 0) {
                    printf("File '%s' removed.\n", filename);
                } else {
                    perror("rm");
                }
            }
        } else {
            printf("Unknown command: %s\n", input);
        }

        free(content);
        content = malloc(1);
        len = 0;
        content[0] = '\0';
    }

    free(content);
    return 0;
}
