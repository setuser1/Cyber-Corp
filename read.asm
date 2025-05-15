section .data
file_in db "output.txt", 0
content times 200 db 0
error_msg db "Error reading file", 0
error_msg_len equ $ - error_msg


section .text
global _start

_start:
    mov rax, 2          ; syscall: sys_open
    lea rdi, [rel file_in]  ; RIP-relative addressing
    mov rsi, 0          ; flags: O_RDONLY
    syscall             ; open the file

    mov rdi, rax       ; save the file descriptor

    mov rax, 0         ; syscall: sys_read
    mov rsi, content   ; buffer to read into
    mov rdx, 100       ; number of bytes to read
    syscall             ; read from the file

    ; Check if read was successful
    cmp rax, 0
    jl .error          ; if rax < 0, jump to error handling
    ; rax now contains the number of bytes read

    ; print the content to stdout
    mov rdx, rax       ; number of bytes read
    mov rax,1
    mov rdi,1
    mov rsi, content
    syscall
    ; close the file    
    mov rax, 3          ; syscall: sys_close
    syscall             ; close the file

    ; exit the program
    mov rax, 60         ; syscall: sys_exit
    xor rdi, rdi        ; exit code 0
    syscall             ; exit the program
.error:
    ; handle error
    mov rax, 1          ; syscall: sys_write
    mov rdi, 2          ; file descriptor: stderr
    lea rdi, [rel file_in]   ; RIP-relative addressing
    lea rsi, [rel error_msg] ; RIP-relative addressing
    mov rdx, error_msg_len
    syscall             ; write the error message

    ; exit the program with error code
    mov rax, 60         ; syscall: sys_exit
    mov rdi, 1          ; exit code 1
    syscall             ; exit the program
