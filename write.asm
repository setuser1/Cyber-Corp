; File: createfile.asm
; Assemble with: nasm -f elf64 createfile.asm && ld -o createfile createfile.o
; Run with: ./createfile
; After running, you should see “output.txt” containing “Hello, world!”

section .data
    filename db  "output.txt", 0      ; null-terminated filename
    msg db  "I hate you people", 10  ; message plus newline
    msg_len equ $ - msg              ; length of the message

section .text
    global _start

_start:
    ; --- sys_open (syscall #2) ---
    mov rax, 2               ; sys_open
    lea rdi, [rel filename]  ; pointer to filename
    mov rsi, 1089             ; flags: O_WRONLY(1) | O_CREAT(64) | O_TRUNC(512) = 577
    mov rdx, 0644            ; mode: rw-r--r-- (octal 0644)
    syscall
    mov rdi, rax            ; save file descriptor

    ; --- sys_write (syscall #1) ---
    mov rax, 1               ; sys_write
    mov rsi, msg             ; pointer to message
    mov rdx, msg_len         ; length of message
    syscall
    ; --- sys_close (syscall #3) ---
    mov rax, 3               ; sys_close
    syscall

    ; --- sys_exit (syscall #60) ---
    mov rax, 60              ; sys_exit
    mov rdi, 80
    syscall
