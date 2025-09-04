#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

int main() {
    // the noob way of printing
    printf("Hello World!\n");
    
    // the pro-way of printing
    char *string = malloc(101);
    strcpy(string, "Hello World!\n");
    write(STDOUT_FILENO, string, strlen(string));
    free(string);

    // the hacker way of printing
    extern void printd(const char* s);
    printd("Hello World!\n");

    // the god way to print something
    long long msg1 = 0x67206D6F6D207275LL;
    long long msg2 = 0x00000000007961LL;
    puts((char*)&msg1);
    
    return 0;
}
