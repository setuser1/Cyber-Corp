#include "servo.h"

#define p 4

void setup() {
    servoAttach(p);
    servosweep(p, 180,90,1,20);
}

void loop() {
    servowrite(p,90);
}
