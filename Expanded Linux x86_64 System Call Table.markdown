# 🧠 Expanded Linux x86_64 System Call Table

**Quick Reference for Linux Syscalls on x86_64**

> **Architecture Note:**  
> In x86_64 Linux, the syscall number is placed in **RAX**, and arguments are passed in registers in the following order: **RDI, RSI, RDX, R10, R8, R9**.

| System Call | Number | Registers                  | Argument Details                                                                                                                                                                                                                   |
|-------------|--------|----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `read`      | 0      | RDI, RSI, RDX              | - **RDI:** file descriptor to read from  
  &nbsp;&nbsp;• Simpler: ID of the file to read from  
  - **RSI:** address of buffer to store read data  
  &nbsp;&nbsp;• Simpler: where the data should be placed  
  - **RDX:** number of bytes to read  
  &nbsp;&nbsp;• Simpler: how many bytes to read                                                                                                           |
| `write`     | 1      | RDI, RSI, RDX              | - **RDI:** file descriptor to write to  
  &nbsp;&nbsp;• Simpler: ID of the file to write to  
  - **RSI:** address of buffer containing data to write  
  &nbsp;&nbsp;• Simpler: where the data you want to write is stored  
  - **RDX:** number of bytes to write  
  &nbsp;&nbsp;• Simpler: how many bytes to write                                                                                                            |
| `open`      | 2      | RDI, RSI, RDX              | - **RDI:** address of the pathname string  
  &nbsp;&nbsp;• Simpler: pointer to the filename (e.g., `"myfile.txt"`)  
  - **RSI:** flags controlling open mode (O_RDONLY, O_WRONLY, etc.)  
  &nbsp;&nbsp;• Simpler: options for opening (read, write, create…)  
  - **RDX:** file mode (permissions) if creating a new file (O_CREAT)  
  &nbsp;&nbsp;• Simpler: permissions for new files (e.g., 0644)                                                               |
| `close`     | 3      | RDI                        | - **RDI:** file descriptor to close  
  &nbsp;&nbsp;• Simpler: ID of the file to close                                                                                                                              |
| `stat`      | 4      | RDI, RSI                   | - **RDI:** address of the pathname string  
  &nbsp;&nbsp;• Simpler: pointer to the filename whose info you want  
  - **RSI:** address of `stat` struct to fill in file info  
  &nbsp;&nbsp;• Simpler: where to put the file’s details (size, perms…)                                                     |
| `mmap`      | 9      | RDI, RSI, RDX, R10, R8, R9 | - **RDI:** desired start address (0 = kernel chooses)  
  &nbsp;&nbsp;• Simpler: where to map memory, or 0 to auto-select  
  - **RSI:** length of mapping in bytes  
  &nbsp;&nbsp;• Simpler: how much memory to map  
  - **RDX:** protection flags (PROT_READ, PROT_WRITE, etc.)  
  &nbsp;&nbsp;• Simpler: what you can do with it (read/write/exec)  
  - **R10:** mapping flags (MAP_SHARED, MAP_PRIVATE, etc.)  
  &nbsp;&nbsp;• Simpler: whether changes are visible to others  
  - **R8:** file descriptor to map, or -1 for anonymous  
  &nbsp;&nbsp;• Simpler: which file to map, or -1 for none  
  - **R9:** offset into file to start mapping  
  &nbsp;&nbsp;• Simpler: where in the file to begin                                                                    |
| `fork`      | 57     | —                          | *(no registers)*  
  &nbsp;&nbsp;• Simpler: duplicate the current process                                                                                                                              |
| `execve`    | 59     | RDI, RSI, RDX              | - **RDI:** address of the program pathname  
  &nbsp;&nbsp;• Simpler: pointer to the new program’s name (e.g., `"/bin/ls"`)  
  - **RSI:** address of argument array (`argv`)  
  &nbsp;&nbsp;• Simpler: list of command-line arguments  
  - **RDX:** address of environment array (`envp`)  
  &nbsp;&nbsp;• Simpler: list of environment variables                                                            |
| `getpid`    | 39     | —                          | *(no registers)*  
  &nbsp;&nbsp;• Simpler: return the current process’s PID                                                                                                                        |
| `kill`      | 62     | RDI, RSI                   | - **RDI:** target process PID  
  &nbsp;&nbsp;• Simpler: ID of the process to signal  
  - **RSI:** signal number (e.g., 9 = SIGKILL)  
  &nbsp;&nbsp;• Simpler: which signal to send (stop/terminate)                                                             |
| `pipe`      | 22     | RDI                        | - **RDI:** address of an int[2] array for two fds  
  &nbsp;&nbsp;• Simpler: where to store the read/write file IDs                                                           |
| `dup`       | 32     | RDI                        | - **RDI:** old file descriptor to duplicate  
  &nbsp;&nbsp;• Simpler: which file ID to copy                                                                              |
| `exit`      | 60     | RDI                        | - **RDI:** exit status code (0 = success, non-zero = error)  
  &nbsp;&nbsp;• Simpler: code indicating success or failure                                                                  |
| `wait`      | 247    | RDI                        | - **RDI:** address to store child exit status  
  &nbsp;&nbsp;• Simpler: where to put the child process’s result                                                            |
