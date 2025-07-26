#include <unistd.h>
#include <string.h>
#include <stdarg.h>

// are you underestimating me?????
void print_string(const char* s) {
    write(1, s, strlen(s));
}
// just like string but needs check yk.
void print_c(const char* s) {
    if (strlen(s) == 1) {
        write(1, s, 1);
    }
}

// hardest js like me
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
    char digit[2];
    for (; i != 0; i /= 10) {
        const int n = i % 10;
        digit[0] = (char)(n + '0');
        digit[1] = '\0';
        strcat(temp, digit);
        pos++;
    }

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

// easy after doing int
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
    char digit[2];
    for (; i != 0; i /= 10) {
        const long long n = i % 10;
        digit[0] = (char)(n + '0');
        digit[1] = '\0';
        strcat(temp, digit);
        pos++;
    }

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

    print_int(int_part);
    write(1, ".", 1);
    const int decimals = 6;
    for (int i = 0; i < decimals; i++) {
        frac_part *= 10;
        const int digit = (int)frac_part;
        char c = (char)(digit + '0');
        write(1, &c, 1);
        frac_part -= digit;
    }
}

// this one sucks
void printd(const char *buff, ...) {
    va_list args;
    va_start(args, buff);

    while (*buff != '\0') {
        if (*buff == '%') {
            buff++;

            if (buff[0] == 'l' && buff[1] == 'l' && buff[2] == 'd') {
                print_long_long(va_arg(args, long long));
                buff += 3;
                continue;
            }

            switch (*buff) {
                case 'd':
                    print_int(va_arg(args, int));
                    break;
                case 's':
                    print_string(va_arg(args, char*));
                    break;
                case 'c':
                    print_c(va_arg(args, char*));
                    break;
                case 'f':
                    print_float(va_arg(args, double));
                    break;
                case '%':
                    write(1, "%", 1);
                    break;
                default:
                    write(1, "%", 1);
                    write(1, buff, 1);
                    break;
            }
        } else {
            write(1, buff, 1);
        }

        buff++;
    }

    va_end(args); // finally
}
