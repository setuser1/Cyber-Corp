import socket
import threading
import pickle
import time
from litrpg_game import (
    Player, assign_quests,
    explore, use_item,
    allocate_stats,
    show_quests, visit_shop,
    revive_teammate, player_turn_done
)

HOST = '0.0.0.0'
PORT = 65432
MAX_PLAYERS = 4

clients = []
players = []
last_heartbeat = {}  # Track last response time
lock = threading.Lock()
turn_index = 0

def save_game(filename="save.pkl"):
    with open(filename, "wb") as f:
        pickle.dump([p.to_dict() for p in players], f)
    print("[SAVE] Game state saved.")

def load_game(filename="save.pkl"):
    global players, clients
    try:
        with open(filename, "rb") as f:
            player_dicts = pickle.load(f)
            players = []
            for data in player_dicts:
                p = Player(data['name'], data.get('role', 'Warrior'))
                p.from_dict(data)
                assign_quests(p)
                players.append(p)
        print(f"[LOAD] Loaded {len(players)} players from save.")
    except Exception as e:
        print(f"[LOAD ERROR] {e}")

def send_data(conn, data):
    try:
        conn.sendall(pickle.dumps(data))
    except Exception as e:
        print(f"[SEND ERROR] {e}")

def recv_data(conn):
    try:
        data = conn.recv(8192)
        if not data:
            return None
        return pickle.loads(data)
    except (ConnectionResetError, EOFError, socket.timeout):
        return None
    except Exception as e:
        print(f"[ERROR recv_data] {e}")
        return None

def remove_player(player):
    global turn_index
    with lock:
        if player in players:
            idx = players.index(player)
            players.pop(idx)
            clients.pop(idx)
            last_heartbeat.pop(player, None)
            print(f"[REMOVED] {player.name} removed from game.")
            if turn_index >= len(players):
                turn_index = 0

def handle_client(conn, addr):
    global turn_index
    print(f"[CONNECTED] {addr}")
    conn.settimeout(60)  # auto-timeout

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
        last_heartbeat[player] = time.time()

    while True:
        if not players:
            break

        with lock:
            if player != players[turn_index]:
                time.sleep(0.1)
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
            remove_player(player)
            break

        last_heartbeat[player] = time.time()
        command = action.get("command")
        log = []

        if command == "explore":
            log = explore(player, players)
        elif command == "use_item":
            item = action.get("item")
            log = use_item(player, item, players)
        elif command == "allocate_stats":
            log = allocate_stats(player)
        elif command == "quests":
            log = show_quests(player)
        elif command == "shop":
            log = visit_shop(player)
        elif command == "revive":
            log = revive_teammate(player, players)
        elif command == "quit":
            print(f"[QUIT] {player.name} has left.")
            send_data(conn, {"type": "info", "msg": "Thanks for playing!"})
            conn.close()
            remove_player(player)
            break
        elif command == "ping":
            # heartbeat ping
            send_data(conn, {"type": "info", "msg": "pong"})
            continue
        else:
            log = ["Unknown command."]

        log += player_turn_done()

        with lock:
            for c, _ in clients:
                send_data(c, {
                    "type": "log",
                    "log": log,
                    "players": [p.to_dict() for p in players]
                })
            turn_index = (turn_index + 1) % len(players)

    conn.close()

def monitor_heartbeats(timeout=90):
    while True:
        time.sleep(10)
        now = time.time()
        with lock:
            to_remove = [p for p, t in last_heartbeat.items() if now - t > timeout]
        for p in to_remove:
            print(f"[TIMEOUT] {p.name} unresponsive.")
            remove_player(p)

def start_server():
    print(f"[STARTING] Server listening on {HOST}:{PORT}")
    threading.Thread(target=monitor_heartbeats, daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            if len(clients) >= MAX_PLAYERS:
                send_data(conn, {"type": "error", "msg": "Server full."})
                conn.close()
                continue
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    start_server()
