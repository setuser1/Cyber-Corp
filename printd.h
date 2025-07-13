#ifndef PRINTD_H
#define PRINTD_H

#include <stdarg.h>

// Your custom printf-like function (supports %d, %s, %c, %%)
void printd(const char *buff, ...);

// Helper functions used internally or externally
void print_int(int i);
void print_string(const char *s);
void print_c(const char *s);
void print_float(double val);  // Optional if you plan to finish this
void print_long_long(long long i);


#endif // PRINTD_H
