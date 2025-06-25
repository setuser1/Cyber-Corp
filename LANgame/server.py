# server.py

import socket
import threading
import pickle
from litrpg_game import (
    Player, assign_quests,
    explore, use_item,
    allocate_stats, show_status,
    show_quests, visit_shop,
    revive_teammate, player_turn_done
)

HOST = '0.0.0.0'
PORT = 65432
MAX_PLAYERS = 4

clients = []
players = []
lock = threading.Lock()
turn_index = 0

def send_data(conn, data):
    try:
        conn.sendall(pickle.dumps(data))
    except:
        pass

def recv_data(conn):
    try:
        return pickle.loads(conn.recv(8192))
    except:
        return None

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
        with lock:
            if players[turn_index] != player:
                continue

        send_data(conn, {
            "type": "turn",
            "player": player.to_dict(),
            "players": [p.to_dict() for p in players],
            "msg": f"It is your turn, {player.name}!"
        })

        action = recv_data(conn)
        if not action:
            print(f"[DISCONNECT] {addr}")
            break

        command = action.get("command")
        log = []

        if command == "explore":
            log = explore(player, players)
        elif command == "use_item":
            item = action.get("item")
            log = use_item(player, item, players)
        elif command == "allocate_stats":
            log = allocate_stats(player)
        elif command == "status":
            log = show_status(player)
        elif command == "quests":
            log = show_quests(player)
        elif command == "shop":
            log = visit_shop(player)
        elif command == "revive":
            log = revive_teammate(player, players)
        elif command == "quit":
            send_data(conn, {"type": "info", "msg": "Thanks for playing!"})
            conn.close()
            break
        else:
            log = ["Unknown command."]

        log += player_turn_done()

        # Broadcast update to all clients
        with lock:
            for c, _ in clients:
                send_data(c, {
                    "type": "log",
                    "log": log,
                    "players": [p.to_dict() for p in players]
                })

            turn_index = (turn_index + 1) % len(players)

    conn.close()

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
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    start_server()
