section .data
filename db "output.txt", 0       ; Null-terminated filename
var db "charlie is good person", 10  ; Message to write (20 bytes)
length equ $ - var                ; Length of message (20 bytes)
filecontent times 100 db 0        ; Buffer for reading (100 bytes)

section .text
global _start

_start:
    ; Open file (syscall 2)
    mov rax, 2                    ; Syscall number for open
    mov rdi, filename             ; Pointer to filename
    mov rsi, 0x100                ; Flags: O_WRONLY (1) | O_CREAT (0x100) | O_TRUNC (0x400)
    mov rdx, 0644                 ; Mode: rw-r--r-- (owner read/write, others read)
    syscall                       ; Invoke open
    mov rbx, rax                  ; Save fd in rbx

    ; Write to file (syscall 1)
    mov rax, 1                    ; Syscall number for write
    mov rdi, rbx                  ; fd from open
    mov rsi, var                  ; Buffer
    mov rdx, length                   ; Length (10 bytes, "charlie is")
    ; mov rdx, length             ; Uncomment for full string (20 bytes)
    syscall                       ; Invoke write

    ; Reset file pointer to start (lseek, syscall 8)
    mov rax, 8                    ; Syscall number for lseek
    mov rdi, rbx                  ; fd
    mov rsi, 0                    ; Offset (0 = start of file)
    mov rdx, 0                    ; Whence: SEEK_SET (0)
    syscall                       ; Invoke lseek

    ; Read from file (syscall 0)
    mov rax, 0                    ; Syscall number for read
    mov rdi, rbx                  ; fd from open
    mov rsi, filecontent          ; Buffer to store data
    mov rdx, 100                  ; Max bytes to read
    syscall                       ; Invoke read
    mov r12, rax                  ; Save bytes read in r12

    ; Close file (syscall 3)
    mov rax, 3                    ; Syscall number for close
    mov rdi, rbx                  ; fd
    syscall                       ; Invoke close

    ; Write to stdout (syscall 1)
    mov rax, 1                    ; Syscall number for write
    mov rdi, 1                    ; fd = 1 (stdout)
    mov rsi, filecontent          ; Buffer with read data
    mov rdx, r12                  ; Bytes to write (from read)
    syscall                       ; Invoke write

    ; Exit (syscall 60)
    mov rax, 60                   ; Syscall number for exit
    mov rdi, 0                    ; Exit status 0
    syscall                       ; Invoke exit
