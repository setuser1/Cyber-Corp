# Expanded Linux x86_64 System Call Table

**Note:** In the x86_64 architecture, the system call number is passed in the RAX register. Arguments are passed in RDI, RSI, RDX, R10, R8, and R9, depending on the system call. Below, each register used by a system call is listed in its own row with its description and a simpler explanation.

| System Call | Number | Register | Argument Description | Simpler Explanation |
|-------------|--------|----------|----------------------|---------------------|
| read        | 0      | RDI      | The file descriptor to read from. This is an integer that identifies the open file. | The ID of the file you want to read from. |
| read        | 0      | RSI      | The address of the buffer where the read data will be stored. | Where to put the data you read, like a box to store it. |
| read        | 0      | RDX      | The number of bytes to read. | How much data to read, e.g., 10 bytes. |
| write       | 1      | RDI      | The file descriptor to write to. | The ID of the file you want to write to. |
| write       | 1      | RSI      | The address of the buffer containing the data to write. | The data you want to write, like pointing to a box holding it. |
| write       | 1      | RDX      | The number of bytes to write. | How much data to write, e.g., 10 bytes. |
| open        | 2      | RDI      | The address of the pathname string. | The name of the file to open, like "myfile.txt". |
| open        | 2      | RSI      | Flags that control how the file is opened (e.g., read-only, write-only, read-write). | Options for opening the file, like read or write mode. |
| open        | 2      | RDX      | The mode, which specifies the permissions if the file is created. Only used if O_CREAT flag is set in RSI. | Permissions for a new file, like who can read or write it, if it’s created. |
| close       | 3      | RDI      | The file descriptor to close. | The ID of the file you want to close. |
| fork        | 57     | -        | No arguments. Creates a new process by duplicating the calling process. | No inputs needed; it just makes a copy of the program. |
| exit        | 60     | RDI      | The exit status of the process. Typically, 0 indicates success, and other values indicate errors. | A number the program sends back to say if it worked (0 usually means success). |
| wait        | 247    | RDI      | The address where the status of the child process will be stored. | A place to store info about how the child process ended. |
| execve      | 59     | RDI      | The address of the pathname string of the new program to execute. | The name of the new program to run, like "/bin/ls". |
| execve      | 59     | RSI      | The address of the array of argument strings (argv). | The list of inputs for the new program, like command-line arguments. |
| execve      | 59     | RDX      | The address of the array of environment strings (envp). | The environment settings for the new program, like variables. |
| mmap        | 9      | RDI      | The starting address for the mapping. Often 0 to let the kernel choose. | Where to start putting the memory, or 0 to let the system decide. |
| mmap        | 9      | RSI      | The length of the mapping in bytes. | How much memory to map, e.g., 4096 bytes. |
| mmap        | 9      | RDX      | Protection flags, like read, write, execute permissions. | What you can do with the memory, like read or write. |
| mmap        | 9      | R10      | Flags that control the mapping, like shared or private. | Options for the mapping, like whether changes are shared. |
| mmap        | 9      | R8       | The file descriptor to map from, or -1 for anonymous mapping. | The ID of the file to map, or -1 if not mapping a file. |
| mmap        | 9      | R9       | The offset into the file to start mapping from. | Where in the file to start mapping, like byte 0. |
| getpid      | 39     | -        | No arguments. Returns the process ID of the calling process. | No inputs needed; it tells you the ID of your program. |
| kill        | 62     | RDI      | The process ID (PID) of the process to send a signal to. | The ID of the program you want to signal. |
| kill        | 62     | RSI      | The signal number to send (e.g., SIGTERM=15, SIGKILL=9). | The signal to send, like “stop” or “end now”. |
| pipe        | 22     | RDI      | The address of an array of 2 integers to store the read and write file descriptors. | A place to store two IDs: one for reading, one for writing. |
| dup         | 32     | RDI      | The old file descriptor to duplicate. | The ID of the file you want to copy. |
| stat        | 4      | RDI      | The address of the pathname string of the file to get info about. | The name of the file to check, like "myfile.txt". |
| stat        | 4      | RSI      | The address of a stat structure to store file information. | Where to put the file’s details, like size or permissions. |

This table includes a variety of system calls for file operations, process management, memory mapping, signal handling, and inter-process communication, with clear descriptions and simple explanations for each argument.