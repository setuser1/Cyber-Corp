import socket

PORT = 90

def _to_bytes(move):              # str ➜ bytes helper
    return move.encode('utf-8') if isinstance(move, str) else move

def server_mode(move: str | bytes, color: str):
    """Host side: listen once, then send OR receive a single move."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', PORT))
        s.listen(1)
        print(f"Server listening on :{PORT} …")
        conn, addr = s.accept()
        with conn:
            print("Connected", addr)
            if color == 'white':
                conn.send(_to_bytes(move))
            else:
                return conn.recv(1024).decode('utf-8')

def client_mode(move: str | bytes, color: str, host: str):
    """Guest side: connect once, then send OR receive a single move."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host.strip(), PORT))
        if color == 'white':
            s.send(_to_bytes(move))
        else:
            return s.recv(1024).decode('utf-8')


def closing(won: bool, lost: bool, draw: bool):
    """No persistent socket to close here; sockets are closed by `with`."""
    if won or lost or draw:
        print("Game ended. All sockets have been closed.")
