#ifndef MANUAL_SERVO_H
#define MANUAL_SERVO_H

#include <Arduino.h>  // For pinMode, digitalWrite, delayMicroseconds

// Servo configuration
#define SERVO_PERIOD 20000  // 20 ms in microseconds

// Convert angle (0-180) to pulse width (microseconds)
static inline int angleToPulse(int angle) {
    if (angle < 0) angle = 0;
    if (angle > 180) angle = 180;
    return 1000 + (angle * 1000) / 180;
}

// Initialize a servo pin
static inline void servoAttach(uint8_t pin) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
}

// Write a servo angle (blocking)
static inline void servowrite(uint8_t pin, int angle) {
    int pulse = angleToPulse(angle) + 115;
    digitalWrite(pin, HIGH);
    delayMicroseconds(pulse);
    digitalWrite(pin, LOW);
    delayMicroseconds(SERVO_PERIOD - pulse);
}

// Sweep servo from startAngle to endAngle
static inline void servosweep(uint8_t pin, int startAngle, int endAngle, int step, int delayMs) {
    if (startAngle < endAngle) {
        for (int a = startAngle; a <= endAngle; a += step) {
            servowrite(pin, a);
            delay(delayMs);
        }
    } else {
        for (int a = startAngle; a >= endAngle; a -= step) {
            servowrite(pin, a);
            delay(delayMs);
        }
    }
}

#endif // MANUAL_SERVO_H

