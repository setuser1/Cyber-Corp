# C~ Language Support for VS Code

This extension adds syntax highlighting and basic editing support for the **C~** programming language in Visual Studio Code.

## Features

- Syntax highlighting for:
  - Keywords (`if`, `xif`, `else`, `while`, `return`, `expr`, etc.)
  - Types (`int`, `char`, `float`, `double`, `void`)
  - Function definitions and calls
  - Variable declarations and assignments
  - Operators and punctuation
  - Numbers, strings, and comments
  - Preprocessor directives (e.g., `#include <stdio.h>`)
- Bracket and parenthesis matching
- Comment toggling (`//` and `/* ... */`)
- Auto-closing pairs for brackets, quotes, and parentheses

## Usage

1. **Manual Installation:**  
   Since this extension is not yet on the VS Code Marketplace, you must install it manually:
   - Download or clone this repository.
   - Run `vsce package` in the extension folder to generate a `.vsix` file (if you don't have `vsce`, install it with `npm install -g @vscode/vsce`).
   - In VS Code, press `Ctrl+Shift+P` and select `Extensions: Install from VSIX...`.
   - Choose the generated `.vsix` file to install.
2. Open any file with the `.C~` extension.
3. Enjoy C~ syntax highlighting and editing features!

## Example

```c
#include <stdio.h>

expr print_menu() {
    printf("Menu\n"):
    printf("1. Add\n"):
    printf("2. Subtract\n"):
    printf("3. Exit\n"):
}

int main() {
    int choice:
    print_menu():
    scanf("%d", &choice):
    if (choice == 1) {
        printf("Add selected\n"):
    }
    xif (choice == 2) {
        printf("Subtract selected\n"):
    }
    else {
        printf("You chose option {choice}\n"):
    }
}
```

## Known Issues

- Some advanced C~ features may not be fully highlighted.
- Only basic editing features are supported.

## Release Notes

### 1.0.0

Initial release of C~ Language Support for VS Code.

---

**Enjoy using C~ in VS Code!**
