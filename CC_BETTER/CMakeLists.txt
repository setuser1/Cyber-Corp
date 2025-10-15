cmake_minimum_required(VERSION 4.0)
project(C_Triangle C)

set(CMAKE_C_STANDARD 11)

add_executable(C_Triangle main.c
        lexer.c
        Pointers_and_Lines.c
        compiler.h
)
