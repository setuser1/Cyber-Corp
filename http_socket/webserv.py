import socket

# Read the HTML file to serve as the main page body
global body_html
with open("index.html", "r") as f:
    body_html = f.read()

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
        
# Main request handler
def handle_request(request, body=body_html):
    # Split the request into lines and parse the request line
    request_lines = request.split("\r\n")
    request_line = request_lines[0]
    method, path, _ = request_line.split()
    method = method.upper()
    # Handle GET requests
    if method == "GET":
        if path == "/":
            # Serve the main HTML page
            return get_header(200, "OK", "text/html", body) + body
        elif path == "/style.css":
            # Serve the CSS file
            with open("style.css", "r") as f:
                css = f.read()
            return get_header(200, "OK", "text/css", css) + css
        else:
            # Serve a 404 Not Found page for unknown paths
            not_found_body = "<html><body><h1>404 Not Found</h1></body></html>"
            return get_header(404, "Not Found", "text/html", not_found_body) + not_found_body
    # Handle POST requests
    elif method == "POST":
        post_body = "<html><body><h1>POST request received!</h1></body></html>"
        return post_header(200, "OK", "text/html", post_body) + post_body
    # Handle OPTIONS requests
    elif method == "OPTIONS":
        options_body = "<html><body><h1>Allowed Methods: GET, POST, OPTIONS</h1></body></html>"
        return get_header(200, "OK", "text/html", options_body) + options_body
    # Handle all other methods (405 Method Not Allowed)
    else:
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
        response = handle_request(request)
        conn.sendall(response.encode('utf-8'))
        conn.close()
if __name__ == "__main__":
    serv()
