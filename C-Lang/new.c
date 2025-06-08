#include <stdio.h>
#include <stdlib.h>

#define BUFFERSIZE 2048
static int n;

int angle() {
    int measure = ((n - 2) * 180) / n;
    return measure;
}


int main() {
    char *buffer = malloc(BUFFERSIZE);
    printf("Enter number of sides: ");
    fgets(buffer, BUFFERSIZE, stdin);

    sscanf(buffer, "%d", &n);

    int result = angle();
    printf("Angle measure: %d°\n", result);

    free(buffer);
    return 0;
}
