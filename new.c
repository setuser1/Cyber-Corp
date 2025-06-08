#include <stdio.h>

int angle(int n, int side) {
    int measure = ((n-2)/side)*180;
    return measure;
}

static int N;

int main() {

    printf("Enter sides: ");
    scanf("%d", &N);

    angle(N,N);

    return 0;
}