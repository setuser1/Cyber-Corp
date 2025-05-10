# C~ Language

C~ is a custom, C and python inspired programming language that compiles to LLVM IR using a Python-based compiler. It features a simplified syntax (using `:` instead of `;`, no format specifiers for `printf`, etc.) and is designed for educational and experimental purposes.

## Features

- C-like syntax with simplified statement endings
- Direct compilation to LLVM IR
- Easy integration with LLVM toolchain and GCC/MinGW for Windows

## Example

```
#include <stdio.h>

expr print() {
    printf("\nThis is a void basically\n"):
}

int main() {
    printf("Print statement\n"):

    int x:
    x = 0:

    while x < 5 {
        printf(x):
        printf(" "):
        x = x + 1:
    }
    printf("\n"):

    int f:
    f = 9:

    int new:
    new = func(x, f):
    printf(new):
    printf("\n"):
    print():

    char list[10]:
    list = "hello":

    printf(list):
    printf("\n"):

    return 0:
}

int func(int a, int b) {
    int add:
    add = a + b:
    return add:
}
```

## How to Run

### Prerequisites

- [Python 3](https://www.python.org/)
- [LLVM tools (llc)](https://llvm.org/)
- [GCC/MinGW-w64](https://www.mingw-w64.org/) (for Windows linking)

### Steps

1. **Write your C~ code**  
   Save your code in a file, e.g., `file.C~`.

2. **Compile to LLVM IR**  
   Use the provided Python compiler ('chatgpt_compiler.py'):
   ```
   python hi.py file.C~
   ```
   This generates `file.ll`.

3. **Compile LLVM IR to object file**  
   ```
   llc -filetype=obj file.ll -o file.o
   ```

4. **Link to create executable**  
   ```
   gcc file.o -o file.exe
   ```

5. **Run your program**  
   ```
   ./file.exe
   ```

## Output Example

```
Print statement
0 1 2 3 4
14
This is a void basically
hello
```

## Notes

- `printf` does **not** use format specifiers in C~. Just pass the value or string directly.
- Use `:` instead of `;` to end statements.
- Strings use double quotes (`"hello"`), not single quotes.

---

**Enjoy experimenting with C~!**