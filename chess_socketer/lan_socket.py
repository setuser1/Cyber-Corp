import socket, time

PORT = 90


def _to_bytes(msg: str | bytes) -> bytes:
    return msg if isinstance(msg, bytes) else msg.encode("utf-8")


def server_mode(msg: str | bytes, color: str) -> str:
    """
    Host side: accept one connection, then either send (`white`) or receive
    (`black`) a single message.  Returns the received string ('' if nothing).
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", PORT))
        s.listen(1)
        conn, _ = s.accept()
        with conn:
            if color == "white":                # host sending
                conn.send(_to_bytes(msg))
                return ""
            else:                               # host receiving
                data = conn.recv(1024)
                return data.decode("utf-8") if data else ""


def client_mode(msg: str | bytes, color: str, host: str) -> str:
    """
    Guest side: keep trying to connect until host is ready, then send
    (`white`) or receive (`black`) one message.
    """
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host.strip(), PORT))
                if color == "white":            # guest sending
                    s.send(_to_bytes(msg))
                    return ""
                else:                           # guest receiving
                    data = s.recv(1024)
                    return data.decode("utf-8") if data else ""
        except (ConnectionRefusedError, ConnectionResetError, OSError):
            time.sleep(0.2)
            continue
