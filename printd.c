#include <unistd.h>
#include <string.h>
#include <stdarg.h>

void print_string(const char* s) {
    write(1, s, strlen(s));
}

void print_c(const char* s) {
    if (strlen(s) == 1) {
        write(1, s, 1);
    }
}


void print_int(int i) {
    if (i == 0) {
        write(1, "0", 1);
        return;
    }
    int pos = 0;
    int negative = 0;
    if (i < 0) {
        negative = 1;
        i = -i;
    }


    char temp[32];

    temp[0] = '\0';
    char digit[2];       // 1 for digit, 1 for null terminator
    for (; i != 0; i /= 10) {
        const int n = i % 10;


        digit[0] = (char)(n + '0');  // convert int to char
        digit[1] = '\0';     // null terminator
        strcat(temp, digit);    // now safe
        pos++;
    }

    // Build final string with correct order
    char final[32];
    int idx = 0;

    if (negative) {
        final[idx++] = '-';
    }

    for (int j = pos - 1; j >= 0; j--) {
        final[idx++] = temp[j];
    }
    final[idx] = '\0';

    print_string(final);
}


void print_long_long(long long i) {
    if (i == 0) {
        write(1, "0", 1);
        return;
    }
    int pos = 0;
    int negative = 0;
    if (i < 0) {
        negative = 1;
        i = -i;
    }


    char temp[32];

    temp[0] = '\0';
    char digit[2];       // 1 for digit, 1 for null terminator
    for (; i != 0; i /= 10) {
        const long long n = i % 10;


        digit[0] = (char)(n + '0');  // convert int to char
        digit[1] = '\0';     // null terminator
        strcat(temp, digit);    // now safe
        pos++;
    }

    // Build final string with correct order
    char final[32];
    int idx = 0;

    if (negative) {
        final[idx++] = '-';
    }

    for (int j = pos - 1; j >= 0; j--) {
        final[idx++] = temp[j];
    }
    final[idx] = '\0';

    print_string(final);
}


void print_float(const double val) {
    int int_part = (int)val;
    double frac_part = val - (double)int_part;
    if (val < 0) {
        write(1, "-", 1);
        int_part = -int_part;
        frac_part = -frac_part;
    }

    print_int(int_part);      // print integer part
    write(1, ".", 1);         // print decimal point
    const int decimals = 6;         // Number of digits after the decimal
    for (int i = 0; i < decimals; i++) {
        frac_part *= 10;
        const int digit = (int)frac_part;
        char c = (char)(digit + '0');
        write(1, &c, 1);
        frac_part -= digit;
    }

}


void printd(const char *buff, ...) {
    va_list args;
    va_start(args, buff);

    while (*buff != '\0') {
        if (*buff == '%') {
            buff++;

            // Handle %lld (long long) first
            if (buff[0] == 'l' && buff[1] == 'l' && buff[2] == 'd') {
                print_long_long(va_arg(args, long long));
                buff += 3;  // Skip 'l', 'l', and 'd'
                continue;
            }

            // Single-character specifiers
            switch (*buff) {
                case 'd':
                    print_int(va_arg(args, int));
                    break;
                case 's':
                    print_string(va_arg(args, char*));
                    break;
                case 'c':
                    print_c(va_arg(args, char*));  // Still using char* (if changed to char, cast from int)
                    break;
                case 'f':
                    print_float(va_arg(args, double));
                    break;
                case '%':
                    write(1, "%", 1);
                    break;
                default:
                    // Unknown format specifier, print it literally
                    write(1, "%", 1);
                    write(1, buff, 1);
                    break;
            }
        } else {
            write(1, buff, 1);
        }

        buff++;
    }

    va_end(args);
}