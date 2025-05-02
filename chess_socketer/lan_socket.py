import socket

# We’ll create a fresh socket for each server/client call,
# to avoid binding/sending on the same socket object multiple times.

def server_mode(move: str, color: str):
    """Listen for one connection, then send or receive the single move."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 90))
        s.listen(1)
        print("Server is listening on host:90...")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            if color == 'white':
                print("White sends move:", move)
                conn.send(move)
            else:
                print("Black waiting for opponent move...")
                data = conn.recv(1024)
                print("Received move:", data.decode('utf-8'))
                return data.decode('utf-8')


def client_mode(move: str, color: str, host: str):
    """Connect to server (prompting IP), then send or receive the single move."""
    host = host.strip()  # Prompt for IP address of the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, 90))
        if color == 'white':
            print("White sends move:", move)
            s.send(move)
        else:
            print("Black waiting for opponent move...")
            data = s.recv(1024)
            print("Received move:", data.decode('utf-8'))
            return data.decode('utf-8')


def closing(won: bool, lost: bool, draw: bool):
    """No persistent socket to close here; sockets are closed by `with`."""
    if won or lost or draw:
        print("Game ended. All sockets have been closed.")
