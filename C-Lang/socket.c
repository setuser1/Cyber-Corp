#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

struct socket_info {
    int socket_fd;
    socklen_t addr_len;
    int port;
};

struct socket_info serv(const char *ip, int port) {
    struct sockaddr_in server_addr;
    struct socket_info info;

    info.socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    info.addr_len = sizeof(server_addr);
    info.port = port;
    if (info.socket_fd < 0) {
        perror("socket creation failed");
        info.socket_fd = -1;
        return info;
    }
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);

    // Set custom IP address
    if (inet_pton(AF_INET, ip, &server_addr.sin_addr) <= 0) {
        perror("invalid IP address");
        close(info.socket_fd);
        info.socket_fd = -1;
        return info;
    }

    if (bind(info.socket_fd, (struct sockaddr *)&server_addr, info.addr_len) < 0) {
        perror("bind failed");
        close(info.socket_fd);
        info.socket_fd = -1;
        return info;
    }

    if (listen(info.socket_fd, 5) < 0) {
        perror("listen failed");
        close(info.socket_fd);
        info.socket_fd = -1;
        return info;
    }

    printf("Server listening on %s:%d\n", ip, port);
    return info;
}

int accept_connection(int socket_fd, struct sockaddr_in *client_addr) {
    socklen_t addr_len = sizeof(*client_addr);
    int client_fd = accept(socket_fd, (struct sockaddr *)client_addr, &addr_len);
    if (client_fd < 0) {
        perror("accept failed");
        return -1;
    }
    return client_fd;
}

int send_response(int client_fd, const char *response) {
    char header[512];
    size_t content_length = strlen(response);
    snprintf(header, sizeof(header),
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n"
        "Content-Length: %zu\r\n"
        "Connection: keep-alive\r\n"
        "\r\n", content_length);

    // Send header
    if (send(client_fd, header, strlen(header), 0) < 0) {
        perror("send header failed");
        return -1;
    }
    // Send body
    if (send(client_fd, response, content_length, 0) < 0) {
        perror("send body failed");
        return -1;
    }
    return 0;
}


int main() {
    struct socket_info server = serv("127.0.0.1", 80);
    if (server.socket_fd < 0) return 1;

    struct sockaddr_in client_addr;
    char input[100];
    printf("Enter the name of the HTML file (without extension): ");
    fgets(input, sizeof(input), stdin);
    input[strcspn(input, "\n")] = 0; // Remove newline

    char filename[128];
    snprintf(filename, sizeof(filename), "%s.html", input);

    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("File not found");
        close(server.socket_fd);
        return 1;
    }

    // Dynamically read file into response buffer
    size_t response_size = 2048;
    char *response = malloc(response_size);
    if (!response) {
        perror("malloc failed");
        fclose(file);
        close(server.socket_fd);
        return 1;
    }

    size_t total_len = 0;
    char buffer[1024];
    
    while (fgets(buffer, sizeof(buffer), file) != NULL) {
        size_t line_len = strlen(buffer);
        if (total_len + line_len + 1 > response_size) {
            size_t new_size = response_size * 2;
            char *new_response = realloc(response, new_size);
            if (!new_response) {
                perror("realloc failed");
                free(response);
                fclose(file);
                close(server.socket_fd);
                return 1;
            }
            response = new_response;
            response_size = new_size;
        }
        strcpy(response + total_len, buffer);
        total_len += line_len;
    }
    response[total_len] = '\0';
    fclose(file);

    int client_fd = accept_connection(server.socket_fd, &client_addr);
    if (client_fd >= 0) {
        printf("Accepted a connection!\n");
        while (1) {
            char request[2048];
            ssize_t bytes = recv(client_fd, request, sizeof(request) - 1, 0);
            if (bytes <= 0) break; // client closed or error

            request[bytes] = '\0';
            // (Optional) Parse the request here

            send_response(client_fd, response); // send the same response each time
        }
        close(client_fd);
    }

    free(response);
    close(server.socket_fd);
    return 0;
}
