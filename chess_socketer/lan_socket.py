import socket
import time

PORT = 90

def _to_bytes(move):
    return move.encode('utf-8') if isinstance(move, str) else move

def server_mode(move: str | bytes, color: str):
    """Host side: listen once, then send OR receive a single move."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', PORT))
        s.listen(1)
        # print(f"Server listening on :{PORT} …")
        conn, addr = s.accept()
        with conn:
            # print("Connected", addr)
            if color == 'white':
                conn.send(_to_bytes(move))
                return ''
            else:
                data = conn.recv(1024)
                return data.decode('utf-8') if data else ''

def client_mode(move: str | bytes, color: str, host: str):
    """Guest side: connect (with retries), then send OR receive a single move."""
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host.strip(), PORT))
                if color == 'white':
                    s.send(_to_bytes(move))
                    return ''
                else:
                    data = s.recv(1024)
                    return data.decode('utf-8') if data else ''
        except (ConnectionRefusedError, ConnectionResetError, OSError):
            time.sleep(0.2)
            continue
