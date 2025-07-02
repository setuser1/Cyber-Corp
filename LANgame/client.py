# ------------------ client.py ------------------
import socket
import pickle
import os

HOST = input("Enter server IP (blank for localhost): ") or "localhost"
PORT = 65432

def send_data(sock, data):
    try:
        sock.sendall(pickle.dumps(data))
    except:
        print("[ERROR] Failed to send data.")

def recv_data(sock):
    try:
        data = sock.recv(8192)
        if not data:
            return None
        return pickle.loads(data)
    except:
        return None

def print_stats(player):
    print(f"{player['name']} the {player['role']} - Level {player['level']}")
    print(f"HP: {player['hp']} / {player['max_hp']}, ATK: {player['attack']}, XP: {player['xp']}/{player['xp_needed']}")
    if player['role'] == "Mage":
        print(f"MP: {player['mana']} / {player['max_mana']}, Spell Power: {player['spell_power']}")
    print(f"Inventory: {player['inventory']}, Gold: {player['gold']}, Stat Points: {player['stat_points']}")

def player_turn(sock, player, players):
    while True:
        print_stats(player)
        print("Your actions:")
        print("1. Explore")
        print("2. Use Item")
        print("3. Allocate Stats")
        print("4. View Quests")
        print("5. Visit Shop")
        print("6. Revive Teammate")
        print("7. Quit Game")
        choice = input("> ").strip()

        if choice == "1":
            send_data(sock, {"command": "explore"})
            break
        elif choice == "2":
            print(f"Inventory: {player['inventory']}")
            item = input("Which item do you want to use? ").strip()
            send_data(sock, {"command": "use_item", "item": item})
            break
        elif choice == "3":
            send_data(sock, {"command": "allocate_stats"})
            break
        elif choice == "4":
            send_data(sock, {"command": "quests"})
            break
        elif choice == "5":
            send_data(sock, {"command": "shop"})
            break
        elif choice == "6":
            send_data(sock, {"command": "revive"})
            break
        elif choice == "7":
            send_data(sock, {"command": "quit"})
            return False
        else:
            print("Invalid input. Try again.")
    return True

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        intro = recv_data(sock)
        print(intro.get("msg", ""))

        name = input("Enter your character's name: ").strip()
        role = input("Choose your class (Warrior/Mage): ").strip().capitalize()
        send_data(sock, {"name": name, "role": role})

        while True:
            data = recv_data(sock)
            if not data:
                print("[DISCONNECTED] Server closed connection.")
                break

            if data["type"] == "info":
                print(data["msg"])
            elif data["type"] == "turn":
                print("
--- YOUR TURN ---")
                if not player_turn(sock, data["player"], data["players"]):
                    break
            elif data["type"] == "log":
                print("
--- GAME LOG ---")
                for line in data["log"]:
                    print(line)

if __name__ == "__main__":
    main()
