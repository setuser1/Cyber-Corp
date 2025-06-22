# server.py (LAN turn-based game server)

import socket
import threading
import pickle
from litrpg_game import Player, assign_quests, explore, use_item

HOST = '0.0.0.0'
PORT = 65432
MAX_PLAYERS = 4

clients = []
players = []
lock = threading.Lock()
turn_index = 0

# Send data to client
def send_data(conn, data):
    try:
        conn.sendall(pickle.dumps(data))
    except:
        pass

# Receive data from client
def recv_data(conn):
    try:
        return pickle.loads(conn.recv(4096))
    except:
        return None

# Handle a single client connection
def handle_client(conn, addr):
    global turn_index

    print(f"[CONNECTED] {addr}")
    send_data(conn, {"type": "info", "msg": "Connected to server. Send your character."})

    player_data = recv_data(conn)
    if not player_data:
        print("[ERROR] Failed to receive player data.")
        conn.close()
        return

    player = Player(player_data['name'], player_data['role'])
    player.from_dict(player_data)
    assign_quests(player)

    with lock:
        players.append(player)
        clients.append((conn, player))

    while True:
        if players[turn_index] != player:
            continue

        send_data(conn, {"type": "turn", "player": player.to_dict(), "players": [p.to_dict() for p in players]})

        action = recv_data(conn)
        if not action:
            print(f"[DISCONNECT] {addr}")
            break

        log = []

        if action["command"] == "explore":
            log = explore(player)
        elif action["command"] == "use_item":
            item = action.get("item")
            log = use_item(player, item, players)
        elif action["command"] == "quit":
            send_data(conn, {"type": "info", "msg": "Thanks for playing!"})
            conn.close()
            break

        # Broadcast log to all players
        with lock:
            for c, _ in clients:
                send_data(c, {"type": "log", "log": log, "players": [p.to_dict() for p in players]})

            turn_index = (turn_index + 1) % len(players)

    conn.close()

# Main server loop

def start_server():
    print(f"[STARTING] Server listening on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            if len(clients) >= MAX_PLAYERS:
                conn.sendall(pickle.dumps({"type": "error", "msg": "Server full."}))
                conn.close()
                continue
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    start_server()
