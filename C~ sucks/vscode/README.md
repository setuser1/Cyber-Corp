# C~ Development with VS Code and `wrapper.py`

This project uses VS Code’s **Debugging** and **Tasks** features to streamline building and running C~ (C-tilde) files through a Python wrapper script. Once configured, you can:

- ▶️ **Build & Run** any `*.c~` file with a single keyboard shortcut  
- 🐞 **Debug** your program inside VS Code with breakpoints, step-through, and variable inspection  

---

## Prerequisites

- **Python 3.x** installed and on your `PATH`  
- **VS Code** (v1.60 or later recommended)  
- [Python extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python)  
- chatgpt_compiler.py

---

## Project Layout

my-project/
├── .vscode/
│ ├── launch.json # Debug configuration
│ └── tasks.json # Build & run task
├── wrapper.py # Python script that compiles & launches C~ code
└── src/
└── example.c~ # Your C~ source files

---

## Debug Configuration (`.vscode/launch.json`)

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Build and Run C~ Program",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/.vscode/wrapper.py",
      "args": ["${file}"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```