#ifndef PRINTD_H
#define PRINTD_H

#include <stdarg.h>

// No more ai comments
void printd(const char *buff, ...);

void print_int(int i);
void print_string(const char *s);
void print_c(const char *s);
void print_float(double val);
void print_long_long(long long i);


#endif
