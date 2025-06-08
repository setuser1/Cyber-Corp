#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int run_shell(char *filename) {
    pid_t pid = fork();

    if (pid == 0) {
        // Child process
        char *argv[] = {filename, NULL};
        char *envp[] = {NULL};
        execve(filename, argv, envp);

        // execve failed if we reach herei thou
        perror("execve failed");
        exit(EXIT_FAILURE);
    } else {
        // Parent process: wait for child to finish
        int status;
        wait(&status);
        return status;
    }
}

int main(int argc, char *argv[]) {
    if (argc == 0) {
        fprintf(stderr, "Usage: %s <shell_path>\n", argv[0]);
        return EXIT_FAILURE;
    }

    char *shell_path = argv[1];

    int status = run_shell(shell_path);

    printf("Shell exited with status %d\n", status);
    return 0;
}
