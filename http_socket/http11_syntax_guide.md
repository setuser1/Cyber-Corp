# HTTP/1.1 Syntax Guide

A concise reference for HTTP/1.1 methods, including request-line syntax, common header descriptions, examples, and Python socket usage.

---

## Table of Contents

- [Common Header Fields](#common-header-fields)
- [OPTIONS](#options)
- [GET](#get)
- [HEAD](#head)
- [POST](#post)
- [PUT](#put)
- [DELETE](#delete)
- [TRACE](#trace)
- [CONNECT](#connect)
- [Python Socket Client Example](#python-socket-client-example)
- [Python Socket Server Example](#python-socket-server-example)

---

## Common Header Fields

| Header Name        | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `Host`             | Specifies the domain name and port number of the server.                    |
| `Accept`           | Specifies acceptable media types for the response.                          |
| `Content-Type`     | Specifies the media type of the request body.                               |
| `Content-Length`   | Specifies the length of the request body in bytes.                          |
| `Authorization`    | Contains credentials for authenticating the client with the server.         |
| `User-Agent`       | Provides information about the client software.                             |
| `Connection`       | Controls whether the network connection stays open.                         |
| `Cache-Control`    | Directives for caching mechanisms.                                          |
| `Transfer-Encoding`| Specifies transfer encoding applied to the body, e.g., `chunked`.           |

---

## OPTIONS

**Purpose:** Request communication options for the target resource.

```http
OPTIONS /api HTTP/1.1
Host: example.com
Accept: */*
```

---

## GET

**Purpose:** Retrieve a representation of the target resource.

```http
GET /index.html HTTP/1.1
Host: www.example.com
Accept: text/html
User-Agent: CustomClient/1.0
```

---

## HEAD

**Purpose:** Same as GET but without the response body.

```http
HEAD /image.png HTTP/1.1
Host: static.example.com
```

---

## POST

**Purpose:** Submit data to be processed.

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json
Content-Length: 44

{"username": "user", "password": "pass"}
```

---

## PUT

**Purpose:** Replace the target resource with the request payload.

```http
PUT /user/1 HTTP/1.1
Host: example.com
Content-Type: application/json
Content-Length: 53

{"id":1, "name": "New Name", "email": "new@example.com"}
```

---

## DELETE

**Purpose:** Remove the target resource.

```http
DELETE /user/1 HTTP/1.1
Host: example.com
Authorization: Bearer token
```

---

## TRACE

**Purpose:** Echo the received request to test the path to the server.

```http
TRACE / HTTP/1.1
Host: example.com
```

---

## CONNECT

**Purpose:** Establish a tunnel to the server.

```http
CONNECT proxy.example.com:443 HTTP/1.1
Host: proxy.example.com:443
```

---

## Python Socket Client Example

```python
import socket

host = 'www.example.com'
port = 80
request = f"""GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"""

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    s.sendall(request.encode())
    response = b""
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        response += chunk

print(response.decode('utf-8', errors='replace'))
```

---

## Python Socket Server Example

```python
import socket
import threading

HOST, PORT = '', 8000
INDEX_FILE = 'index.html'

try:
    with open(INDEX_FILE, 'rb') as f:
        INDEX_CONTENT = f.read()
except FileNotFoundError:
    INDEX_CONTENT = b'<h1>404 Not Found</h1>'

RESPONSE_200 = (
    b'HTTP/1.1 200 OK\r\n'
    b'Content-Type: text/html; charset=utf-8\r\n'
    b'Content-Length: ' + str(len(INDEX_CONTENT)).encode() + b'\r\n'
    b'Connection: close\r\n'
    b'\r\n' + INDEX_CONTENT
)

RESPONSE_404 = (
    b'HTTP/1.1 404 Not Found\r\n'
    b'Content-Type: text/html; charset=utf-8\r\n'
    b'Content-Length: 22\r\n'
    b'Connection: close\r\n'
    b'\r\n'
    b'<h1>404 Not Found</h1>'
)


def handle_client(conn, addr):
    request = conn.recv(1024).decode('utf-8', errors='replace')
    lines = request.split('\r\n')
    if not lines:
        conn.close()
        return
    method, path, _ = lines[0].split(' ', 2)

    if method == 'GET' and path in ('/', '/index.html'):
        conn.sendall(RESPONSE_200)
    else:
        conn.sendall(RESPONSE_404)
    conn.close()


def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f'Serving HTTP on port {PORT} (socket-based)...')
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    run_server()
```

*End of HTTP/1.1 Methods Reference*