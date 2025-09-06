#include <stdint.h>

// Base addresses for GPIO registers
#define GPIO_OUT_W1TS_REG   0x3FF44008  // Write 1 to set pins HIGH
#define GPIO_OUT_W1TC_REG   0x3FF4400C  // Write 1 to clear pins (LOW)
#define GPIO_ENABLE_W1TS_REG 0x3FF44024 // Set pins as OUTPUT
#define GPIO_ENABLE_W1TC_REG 0x3FF44028 // Set pins as INPUT

// Volatile pointers
volatile uint32_t *gpio_out_set   = (volatile uint32_t *)GPIO_OUT_W1TS_REG;
volatile uint32_t *gpio_out_clr   = (volatile uint32_t *)GPIO_OUT_W1TC_REG;
volatile uint32_t *gpio_out_en_set = (volatile uint32_t *)GPIO_ENABLE_W1TS_REG;

// Pin number for LED
#define LED_PIN 2

void setup() {
  // Set GPIO2 as output
  *gpio_out_en_set = (1 << LED_PIN);
}

void loop() {
  // Turn LED ON
  *gpio_out_set = (1 << LED_PIN);
  delay(500);

  // Turn LED OFF
  *gpio_out_clr = (1 << LED_PIN);
  delay(500);
}
