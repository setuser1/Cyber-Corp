#ifndef PRINTD_H
#define PRINTD_H
#include <stdarg.h> // useless in clion

#ifdef __cplusplus
extern "C" {
#endif

    /**
     * @brief Custom version of printf by yours truly. It lacks many of the features.
     * @param format The format.
     * @param ...    Additional arguments depending on format specifiers.
     */
    void printd(const char *format, ...);

    /**
     * @brief Prints an integer.
     */
    void print_int(int value);

    /**
     * @brief Prints a string.
     */
    void print_string(const char *str);

    /**
     * @brief Print a single character.
     *        Is equal to the string func but checks for length to be 1.
     */
    void print_c(const char *str);

    /**
     * @brief Prints a double type along with a float type if needed.
     */
    void print_float(double value);

    /**
     * @brief Print a long-long integer.
     */
    void print_long_long(long long value);

#ifdef __cplusplus
}
#endif

#endif PRINTD_H
