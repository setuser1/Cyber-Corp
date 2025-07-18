#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include "printd.h"

int main() {
    // the pro way of printing
    char *string = malloc(101);
    strcpy(string, "Hello World!");
    write(STDOUT_FILENO, string, strlen(string));
    free(string);

    // the noob way of printing
    printf("Hello World!");

    // the hacker way of printing    
    printd("Hello World!");
    return 0;
}
