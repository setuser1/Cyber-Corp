# 🧠 Expanded Linux x86_64 System Call Table

**Quick Reference for Linux Syscalls on x86_64**

> **Architecture Note:**  
> In x86_64 Linux, the syscall number is placed in **RAX**, and up to six arguments are passed in **RDI, RSI, RDX, R10, R8, R9**.

| System Call | Number | Registers              | Argument Description                                                                                                                | Simpler Explanation                                               |
|-------------|--------|------------------------|--------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| `read`      | 0      | RDI, RSI, RDX          | **RDI:** file descriptor to read from<br>**RSI:** address of buffer to store read data<br>**RDX:** number of bytes to read            | **RDI:** which file to read from<br>**RSI:** where to put data<br>**RDX:** how many bytes to read |
| `write`     | 1      | RDI, RSI, RDX          | **RDI:** file descriptor to write to<br>**RSI:** address of buffer containing data<br>**RDX:** number of bytes to write               | **RDI:** which file to write to<br>**RSI:** where the data is<br>**RDX:** how many bytes to write |
| `open`      | 2      | RDI, RSI, RDX          | **RDI:** pointer to pathname string<br>**RSI:** flags (e.g. O_RDONLY, O_CREAT)<br>**RDX:** mode/permissions if creating a new file   | **RDI:** name of file<br>**RSI:** open options<br>**RDX:** file permissions |
| `close`     | 3      | RDI                    | **RDI:** file descriptor to close                                                                                                    | **RDI:** which file to close                                       |
| `stat`      | 4      | RDI, RSI               | **RDI:** pointer to pathname string<br>**RSI:** pointer to `stat` struct to fill with file info                                      | **RDI:** name of file to inspect<br>**RSI:** where to store its info |
| `mmap`      | 9      | RDI, RSI, RDX, R10, R8, R9 | **RDI:** desired start address (0 = kernel chooses)<br>**RSI:** length in bytes<br>**RDX:** protection flags<br>**R10:** mapping flags<br>**R8:** file descriptor or –1 for anonymous<br>**R9:** offset in file | **RDI:** where to map (or 0)<br>**RSI:** how much memory<br>**RDX:** read/write/exec?<br>**R10:** shared or private?<br>**R8:** file ID or none<br>**R9:** where in the file |
| `fork`      | 57     | –                      | *(no arguments)*                                                                                                                     | duplicates the current process                                     |
| `execve`    | 59     | RDI, RSI, RDX          | **RDI:** pointer to program pathname<br>**RSI:** pointer to `argv` array<br>**RDX:** pointer to `envp` array                           | **RDI:** which program to run<br>**RSI:** its command-line args<br>**RDX:** its environment |
| `getpid`    | 39     | –                      | *(no arguments)*                                                                                                                     | returns current process ID                                         |
| `kill`      | 62     | RDI, RSI               | **RDI:** target PID<br>**RSI:** signal number (e.g. 9 = SIGKILL)                                                                     | **RDI:** which process to signal<br>**RSI:** which signal to send  |
| `pipe`      | 22     | RDI                    | **RDI:** pointer to int[2] array to receive read/write fds                                                                          | **RDI:** where to put the two new file IDs                         |
| `dup`       | 32     | RDI                    | **RDI:** old file descriptor to duplicate                                                                                            | **RDI:** which file ID to copy                                     |
| `exit`      | 60     | RDI                    | **RDI:** exit status code (0 = success, non-zero = error)                                                                            | **RDI:** code indicating success or failure                       |
| `wait`      | 247    | RDI                    | **RDI:** pointer to int where child’s exit status will be stored                                                                     | **RDI:** where to put the child’s exit code                        |
