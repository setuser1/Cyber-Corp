#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

struct sockaddr_in {
    unsigned short sin_family; // Address family (AF_INET)
    unsigned short sin_port;   // Port number (in network byte order)
    struct in_addr sin_addr;   // Internet address (IP address)
    char sin_zero[8];          // Padding to make the structure size equal to sockaddr
};

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

int main() {
    struct socket_info server = serv("127.0.0.1", 8080);
    if (server.socket_fd < 0) return 1;

    struct sockaddr_in client_addr;
    int client_fd = accept_connection(server.socket_fd, &client_addr);
    if (client_fd >= 0) {
        printf("Accepted a connection!\n");
        close(client_fd);
    }

    close(server.socket_fd);
    return 0;
}
