#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

int main() {
    char *string = malloc(101);
    strcpy(string, "Hello World!");
    write(STDOUT_FILENO, string, strlen(string));
    free(string);

    // the noob way of printing
    printf("Hello World!);
    
    return 0;
}
