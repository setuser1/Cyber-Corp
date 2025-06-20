import socket
import threading

SERVER_IP = input("Enter server IP address: ").strip()
PORT = 65432

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024)
            if msg:
                print(f"\n[SERVER] {msg.decode()}\n> ", end="")
        except:
            print("\n[ERROR] Lost connection to server.")
            break

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((SERVER_IP, PORT))
            print(f"[CONNECTED] Connected to server at {SERVER_IP}:{PORT}")

            threading.Thread(target=receive_messages, args=(s,), daemon=True).start()

            while True:
                msg = input("> ").strip()
                if msg.lower() in ("exit", "quit"):
                    break
                s.sendall(msg.encode())

        except ConnectionRefusedError:
            print("[ERROR] Could not connect to server.")
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
