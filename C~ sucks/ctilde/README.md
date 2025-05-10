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

1. Install this extension.
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
    } xif (choice == 2) {
        printf("Subtract selected\n"):
    } else {
        printf("Exit\n"):
    }
}
```


## How to install

download the ctilde.vsix and open visual studio
then open the command palette and look for Extentsions: Install via Vsix
find the file you downloaded and give it to the prompt
you are now done.


## Working with Markdown

You can author your README using Visual Studio Code. Here are some useful editor keyboard shortcuts:

* Split the editor (`Cmd+\` on macOS or `Ctrl+\` on Windows and Linux).
* Toggle preview (`Shift+Cmd+V` on macOS or `Shift+Ctrl+V` on Windows and Linux).
* Press `Ctrl+Space` (Windows, Linux, macOS) to see a list of Markdown snippets.

## For more information

* [Visual Studio Code's Markdown Support](http://code.visualstudio.com/docs/languages/markdown)
* [Markdown Syntax Reference](https://help.github.com/articles/markdown-basics/)

**Enjoy!**
