#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

int main() {
    // the pro-way of printing
    char *string = malloc(101);
    strcpy(string, "Hello World!\n");
    write(STDOUT_FILENO, string, strlen(string));
    free(string);

    // the noob way of printing
    printf("Hello World!\n");

    // the hacker way of printing
    extern void printd(const char* s);
    printd("Hello World!\n");
    return 0;
}
