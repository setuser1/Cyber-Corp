import socket
import threading

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 65432      # Port to listen on

clients = []

def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.sendall(message)
            except:
                clients.remove(client)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    clients.append(conn)
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"[{addr}] {data.decode()}")
            broadcast(data, sender_socket=conn)
    except ConnectionResetError:
        print(f"[DISCONNECT] {addr} disconnected.")
    finally:
        conn.close()
        clients.remove(conn)

def start_server():
    print("[STARTING] Server is starting...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[LISTENING] Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    start_server()
