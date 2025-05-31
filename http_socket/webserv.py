import socket
import os

# Read the HTML file to serve as the main page body
global body_html
homepage = str(input("Enter the name of the HTML file to serve (without .html): ")).strip()

try:
    with open(f"{homepage}.html", "r") as f:
        body_html = f.read()
except:
    body_html = None

CONTENT_TYPES = {
    ".css": "text/css",
    ".html": "text/html",
    ".js": "application/javascript",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".ico": "image/x-icon",
    ".txt": "text/plain"  # <-- Add this line
}

def get_content_type(filename):
    for ext, ctype in CONTENT_TYPES.items():
        if filename.endswith(ext):
            return ctype
    return "application/octet-stream"

# Function to generate HTTP headers for GET responses
def get_header(status_code, status_header, content_type, body):
    return f"HTTP/1.1 {status_code} {status_header}\r\n" \
           f"Content-Type: {content_type}\r\n" \
           f"Content-Length: {len(body)}\r\n" \
           "Connection: close\r\n\r\n"

# Function to generate HTTP headers for POST responses
def post_header(status_code, status_header, content_type, body):
    return f"HTTP/1.1 {status_code} {status_header}\r\n" \
           f"Content-Type: {content_type}\r\n" \
           f"Content-Length: {len(body)}\r\n" \
           "Connection: close\r\n\r\n"
        
# Main request handler using match-case (Python 3.10+)
def handle_request(request, body=body_html):
    # Split the request into lines and parse the request line
    request_lines = request.split("\r\n")
    request_line = request_lines[0]
    method, path, _ = request_line.split()
    method = method.upper()

    match method:
        case "GET":
            match path:
                case "/":
                    # Serve the main HTML page
                    return get_header(200, "OK", "text/html", body) + body
                case p if p.endswith(tuple(CONTENT_TYPES.keys())):
                    # Serve static files (CSS, JS, images, etc.)
                    file = path.lstrip("/")
                    try:
                        content_type = get_content_type(file)
                        mode = "rb" if content_type.startswith("image") else "r"
                        with open(file, mode) as f:
                            file_content = f.read()
                        if mode == "rb":
                            header = get_header(200, "OK", content_type, file_content)
                            response = header.encode('utf-8') + file_content
                            return response
                        else:
                            return get_header(200, "OK", content_type, file_content) + file_content
                    except Exception:
                        not_found_body = "<html><body><h1>404 Not Found</h1></body></html>"
                        return get_header(404, "Not Found", "text/html", not_found_body) + not_found_body
                case _:
                    # Serve a 404 Not Found page for unknown paths
                    not_found_body = "<html><body><h1>404 Not Found</h1></body></html>"
                    return get_header(404, "Not Found", "text/html", not_found_body) + not_found_body
        case "POST":
            post_body = "<html><body><h1>POST request received!</h1>"
            return post_header(200, "OK", "text/html", post_body) + post_body, request_lines[-1]  # Echo the last line of the request as a response
        case "OPTIONS":
            options_body = "<html><body><h1>Allowed Methods: GET, POST, OPTIONS</h1></body></html>"
            return get_header(200, "OK", "text/html", options_body) + options_body
        case _:
            not_allowed_body = "<html><body><h1>405 Method Not Allowed</h1></body></html>"
            return get_header(405, "Method Not Allowed", "text/html", not_allowed_body) + not_allowed_body

# Function to start the server
def serv(port=80, host='127.0.0.1'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"Server running on {host}:{port}")
    while True:
        conn, addr = s.accept()
        print(f"Connection from {addr}")
        request = conn.recv(1024).decode('utf-8')
        if not request:
            continue
        print(f"Request: {request}")
        result = handle_request(request)
        if isinstance(result, tuple):
            response, user_info = result
            # Clean user_info in one line
            user_info = user_info.replace("[", "").replace("]", "").replace("{", "").replace("}", "") \
                .replace("(", "").replace(")", "").replace("'", "").replace('"', "").replace(" ", "").replace(",", " ").replace(":", " = ").split()
            print(f"User Info: {user_info}")
            # Check if userinfo.txt exists, remove if so, then write new
            if os.path.exists("userinfo.txt"):
                os.remove("userinfo.txt")
            with open("userinfo.txt", "w") as f:
                f.write(str(user_info))
        else:
            response = result
        # If response is bytes (for images), send as-is, else encode
        if isinstance(response, bytes):
            conn.sendall(response)
        else:
            conn.sendall(response.encode('utf-8'))
        conn.close()

if __name__ == "__main__":
    serv(80, "0.0.0.0")
