# client.py (LAN multiplayer turn-based game client)

import socket
import pickle
import os
from litrpg_game import Player

SERVER_IP = input("Enter server IP address: ").strip()
PORT = 65432

player = None

def send_data(sock, data):
    try:
        sock.sendall(pickle.dumps(data))
    except:
        print("[ERROR] Failed to send data.")

def recv_data(sock):
    try:
        return pickle.loads(sock.recv(4096))
    except:
        return None

def show_status(player_data):
    print(f"\nName: {player_data['name']} ({player_data['role']})")
    print(f"Level: {player_data['level']}  XP: {player_data['xp']}")
    print(f"HP: {player_data['hp']}/{player_data['max_hp']}  Gold: {player_data['gold']}")
    if player_data['role'] == "Mage":
        print(f"Mana: {player_data['mana']}/{player_data['max_mana']}  Spell Power: {player_data['spell_power']}")
    print(f"Attack: {player_data['attack']}  Bleed Chance: {player_data['bleed_chance']}%")
    print(f"Inventory: {player_data['inventory'] if player_data['inventory'] else 'Empty'}")

def choose_action():
    print("\nWhat would you like to do?")
    print("1. Explore")
    print("2. Use Inventory")
    print("3. Quit Game")
    return input("Choose an option (1-3): ").strip()

def choose_item(inventory):
    print("\n==== Inventory ====")
    for idx, item in enumerate(inventory, 1):
        print(f"{idx}. {item}")
    choice = input("Choose an item to use (or Enter to cancel): ").strip()
    if not choice.isdigit():
        return None
    idx = int(choice) - 1
    if 0 <= idx < len(inventory):
        return inventory[idx]
    return None

def main():
    global player
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((SERVER_IP, PORT))
        except:
            print("[ERROR] Could not connect to server.")
            return

        print("[CONNECTED] Connected to the server.")

        welcome = recv_data(sock)
        if welcome and welcome.get("type") == "info":
            print(welcome["msg"])

        name = input("Enter your character name: ")
        role = input("Choose your class (Warrior/Mage): ").strip().capitalize()
        if role not in ["Warrior", "Mage"]:
            role = "Warrior"

        player = Player(name, role)
        send_data(sock, player.to_dict())

        while True:
            data = recv_data(sock)
            if not data:
                print("[DISCONNECTED] Server closed the connection.")
                break

            if data["type"] == "turn":
                player_data = data["player"]
                all_players = data["players"]
                show_status(player_data)

                while True:
                    action = choose_action()
                    if action == '1':
                        send_data(sock, {"command": "explore"})
                        break
                    elif action == '2':
                        item = choose_item(player_data["inventory"])
                        if item:
                            send_data(sock, {"command": "use_item", "item": item})
                            break
                    elif action == '3':
                        send_data(sock, {"command": "quit"})
                        return
                    else:
                        print("Invalid option.")

            elif data["type"] == "log":
                for line in data["log"]:
                    print(line)

            elif data["type"] == "info":
                print(data["msg"])

if __name__ == "__main__":
    main()
