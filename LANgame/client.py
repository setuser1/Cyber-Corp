# client.py (LAN turn-based game client)

import socket
import pickle
from litrpg_game import Player

SERVER_IP = input("Enter server IP address: ").strip()
PORT = 65432

# Connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((SERVER_IP, PORT))
except Exception as e:
    print(f"[ERROR] {e}")
    exit()

def send_data(data):
    client.sendall(pickle.dumps(data))

def recv_data():
    try:
        return pickle.loads(client.recv(4096))
    except:
        return None

# Create character
print("\n=== Character Creation ===")
name = input("Enter your character name: ")
role = input("Enter your class (Warrior or Mage): ").strip().capitalize()
if role not in ["Warrior", "Mage"]:
    role = "Warrior"

player = Player(name, role)
send_data(player.to_dict())

print("\n[CONNECTED] Waiting for your turn...")

# Game loop
while True:
    data = recv_data()
    if not data:
        print("[ERROR] Disconnected from server.")
        break

    if data["type"] == "info":
        print(data["msg"])

    elif data["type"] == "turn":
        print("\n=== Your Turn ===")
        p = Player(data["player"]["name"], data["player"]["role"])
        p.from_dict(data["player"])

        # Show player status
        print(f"\n{p.name} the {p.role} (Level {p.level})")
        print(f"HP: {p.hp}/{p.max_hp}  Gold: {p.gold}")
        if p.role == "Mage":
            print(f"Mana: {p.mana}/{p.max_mana}  Spell Power: {p.spell_power}")
        print("Inventory:", p.inventory or "Empty")

        print("\nActions:")
        print("1. Explore")
        print("2. Use Item")
        print("3. Quit")

        cmd = input("Choose action (1-3): ").strip()

        if cmd == '1':
            send_data({"command": "explore"})

        elif cmd == '2':
            if not p.inventory:
                print("You have no items.")
                send_data({"command": "none"})
                continue
            print("\nInventory:")
            for idx, item in enumerate(p.inventory, 1):
                print(f"{idx}. {item}")
            choice = input("Choose item to use (or press Enter to cancel): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(p.inventory):
                item = p.inventory[int(choice) - 1]
                send_data({"command": "use_item", "item": item})
            else:
                print("Cancelled.")
                send_data({"command": "none"})

        elif cmd == '3':
            send_data({"command": "quit"})
            print("Exiting game...")
            break
        else:
            send_data({"command": "none"})

    elif data["type"] == "log":
        print("\n--- Turn Result ---")
        for line in data["log"]:
            print(line)

client.close()
