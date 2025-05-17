BITS 64

; filepath: c:\Users\tink\Documents\words\shellexample.asm
; Assembly code to launch a shell using execve (Linux example)

section .data
    shell_path db "/bin/sh", 0  ; Path to the shell
    argv dq shell_path, 0      ; Arguments array (null-terminated)
    envp dq 0                  ; Environment pointer (null)

section .text
    global _start

_start:
    ; syscall: execve(const char *pathname, char *const argv[], char *const envp[])
    mov rax, 59                ; syscall number for execve
    lea rdi, [rel shell_path]  ; pointer to shell path
    lea rsi, [rel argv]        ; pointer to arguments array
    lea rdx, [rel envp]        ; pointer to environment array
    syscall                    ; invoke the system call

    ; Exit if execve fails
    mov rax, 60                ; syscall number for exit
    xor rdi, rdi               ; exit code 0
    syscall

