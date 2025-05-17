; This program demonstrates the use of fork and execve system calls in x86_64 assembly
BITS 64

section .data
    process_name db "./shell", 0  ; Path to the executable
    arg1 db "./shell", 0          ; Argument for the executable
    argv dq arg1, 0               ; Arguments array (null-terminated)
    envp dq 0                     ; Environment pointer (null)
    exitmsg db "Time's up for you buddy.", 10 ; Message to write
    pid dq 0                      ; Placeholder for process ID
    timespec dq 30, 0             ; 30 seconds, 0 nanoseconds

section .text
    global _start

_start:
    ; Fork the process
    mov rax, 57         ; syscall: fork
    syscall             ; fork the process

    test rax, rax       ; Check if we are in the child process
    jz child_process    ; If rax == 0, jump to child process

    ; Parent process
parent_process:
    mov qword [pid], rax ; Store the child process ID in memory

    ; Wait for 30 seconds
    mov rax, 35                    ; syscall: nanosleep
    lea rdi, [rel timespec]        ; Pointer to the timespec structure
    xor rsi, rsi                   ; No remaining time pointer
    syscall                        ; Sleep for 30 seconds

    ; Kill the child process
    mov rax, 62         ; syscall: kill
    mov rdi, [pid]      ; Load the child process ID
    mov rsi, 9          ; Signal: SIGKILL
    syscall             ; Send SIGKILL to the child process

    ; Write a message to stdout
    mov rax, 1          ; syscall: write
    mov rdi, 1          ; File descriptor: stdout
    lea rsi, [rel exitmsg] ; Pointer to the message
    mov rdx, 256 ; Message length
    syscall             ; Write the message

    ; Exit the parent process
    mov rax, 60         ; syscall: exit
    xor rdi, rdi        ; Exit code 0
    syscall

child_process:
    ; Child process: execute ./shell
    mov rax, 59         ; syscall: execve
    lea rdi, [rel process_name] ; Pointer to the filename
    lea rsi, [rel argv] ; Pointer to the argument list
    lea rdx, [rel envp] ; Pointer to the environment list
    syscall             ; Execute the process

    ; If execve fails, exit the child process
    mov rax, 60         ; syscall: exit
    xor rdi, rdi        ; Exit code 0
    syscall