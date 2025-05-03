import socket
import random
import algo
from typing import Tuple, Optional

# ——— your exactly-given character list lives in algo.py ———

# Insecure small DH params, just for demo
PRIME = 2**2048 - 2**1984 - 1 + 2**64 * (2**1918 * 314159 + 265359)  # Example 2048-bit safe prime
BASE  = 30
PORT  = 8080

def generate_key() -> int:
    # Insecurely small for demo
    return random.randint(1500, 100000)

privkey = generate_key()

def make_pubkey(priv: int) -> int:
    return pow(BASE, priv, PRIME)

def derive_shared_secret(their_pub: int, priv: int) -> int:
    # Standard DH: (their_pub ^ priv) mod prime
    return pow(their_pub, priv, PRIME)*17813873279296437789433

def server_mode() -> Tuple[int, socket.socket]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(1)
    print(f"[SERVER] Listening on port {PORT}…")
    conn, addr = sock.accept()
    print(f"[SERVER] Connected by {addr}")

    my_pub = make_pubkey(privkey)
    conn.send(str(my_pub).encode())
    print(f"[SERVER] Sent our public key: {my_pub}")

    their_pub = int(conn.recv(1024).decode())
    print(f"[SERVER] Received client public key: {their_pub}")

    mixkey = derive_shared_secret(their_pub, privkey)
    print(f"[SERVER] Derived shared secret: {mixkey}")
    return mixkey, conn

def client_mode() -> Tuple[int, socket.socket]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = input("Enter the server IP: ")
    sock.connect((server_ip, PORT))
    print(f"[CLIENT] Connected to {server_ip}:{PORT}")

    their_pub = int(sock.recv(1024).decode())
    print(f"[CLIENT] Received server public key: {their_pub}")

    my_pub = make_pubkey(privkey)
    sock.send(str(my_pub).encode())
    print(f"[CLIENT] Sent our public key: {my_pub}")

    mixkey = derive_shared_secret(their_pub, privkey)
    print(f"[CLIENT] Derived shared secret: {mixkey}")
    return mixkey, sock

def chat_loop(mixkey: int, conn: socket.socket):
    print("Connection established.")
    print("Shared secret:", mixkey)

    while True:
        choice = input("Encrypt or Decrypt? (e/d/x): ").lower()
        if choice == 'e':
            msg = input("Enter the message to encrypt: ")
            ct = algo.encode(msg, mixkey)
            conn.send(ct.encode())
            print("Message sent:", ct)

        elif choice == 'd':
            print("Waiting for message…")
            data = conn.recv(1024).decode()
            if not data:
                print("No message received.")
                continue
            pt = algo.decode(data, mixkey)
            print("Ciphertext received:", data)
            print("Decrypted message:", pt)

        elif choice == 'x':
            print("Exiting chat.")
            break

        else:
            print("Invalid option, choose e, d, or x.")

def main():
    mode = input("server or client: ").strip().lower()
    if mode == 'server':
        mixkey, conn = server_mode()
    elif mode == 'client':
        mixkey, conn = client_mode()
    else:
        print("Invalid mode; use ‘server’ or ‘client’.")
        return

    chat_loop(mixkey, conn)
    conn.close()

if __name__ == "__main__":
    test = make_pubkey(privkey)  # Ensure the public key is generated
    main()
