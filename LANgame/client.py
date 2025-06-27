import socket
import pickle
import os
import threading
import time

SERVER_PORT = 65432

def send_data(sock, data):
    try:
        sock.sendall(pickle.dumps(data))
    except:
        print("[ERROR] Failed to send data.")

def recv_data(sock):
    try:
        return pickle.loads(sock.recv(8192))
    except:
        return None

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_character():
    name = input("Enter your character's name: ").strip()
    role_input = input("Choose your class: (1) Warrior (2) Mage: ").strip()
    role = "Mage" if role_input == "2" else "Warrior"
    return {"name": name, "role": role}

def display_player(player):
    print(f"\n=== {player['name']} ({player['role']}) ===")
    print(f"Level: {player['level']} | XP: {player['xp']} | Gold: {player['gold']}")
    print(f"HP: {player['hp']}/{player['max_hp']}")
    if player['role'] == "Mage":
        print(f"Mana: {player['mana']}/{player['max_mana']} | Spell Power: {player['spell_power']}")
    print(f"Attack: {player['attack']} | Bleed Chance: {player['bleed_chance']}%")
    print(f"Inventory: {player['inventory'] if player['inventory'] else 'Empty'}")
    print(f"Stat Points: {player['stat_points']}")

def show_menu():
    print("\n=== MENU ===")
    print("1. Explore")
    print("2. Use Item")
    print("3. Allocate Stats")
    print("4. Show Quests")
    print("5. Visit Shop")
    print("6. Revive Teammate")
    print("7. Quit")

def choose_item(inventory):
    if not inventory:
        print("You have no items.")
        return None
    print("\nYour Inventory:")
    for i, item in enumerate(inventory, 1):
        print(f"{i}. {item}")
    choice = input("Choose item number to use (or press Enter to cancel): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(inventory)):
        return None
    return inventory[int(choice) - 1]

def heartbeat_loop(sock):
    while True:
        try:
            time.sleep(30)
            send_data(sock, {"command": "ping"})
        except:
            break

def client_main():
    server_ip = input("Enter server IP address: ").strip()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, SERVER_PORT))
            print("[CONNECTED]")

            # Start heartbeat thread
            threading.Thread(target=heartbeat_loop, args=(s,), daemon=True).start()

            welcome = recv_data(s)
            print(welcome["msg"])

            player_data = create_character()
            send_data(s, player_data)

            while True:
                response = recv_data(s)
                if not response:
                    print("[DISCONNECTED]")
                    break

                if response["type"] == "turn":
                    clear()
                    player = response["player"]
                    players = response["players"]

                    display_player(player)
                    show_menu()

                    while True:
                        cmd = input("Choose an action: ").strip()
                        if cmd == "1":
                            send_data(s, {"command": "explore"})
                            break
                        elif cmd == "2":
                            item = choose_item(player["inventory"])
                            if item:
                                send_data(s, {"command": "use_item", "item": item})
                                break
                        elif cmd == "3":
                            send_data(s, {"command": "allocate_stats"})
                            break
                        elif cmd == "4":
                            send_data(s, {"command": "quests"})
                            break
                        elif cmd == "5":
                            send_data(s, {"command": "shop"})
                            break
                        elif cmd == "6":
                            send_data(s, {"command": "revive"})
                            break
                        elif cmd == "7":
                            send_data(s, {"command": "quit"})
                            print("Goodbye!")
                            return
                        else:
                            print("Invalid input.")

                elif response["type"] == "log":
                    clear()
                    print("\n=== Battle Log ===")
                    for line in response["log"]:
                        print(line)
                    print("\n=== Updated Player Status ===")
                    for p in response["players"]:
                        print(f"{p['name']} - HP: {p['hp']}/{p['max_hp']} | Gold: {p['gold']} | XP: {p['xp']}")
                    input("\nPress Enter to continue...")

                elif response["type"] == "info":
                    print(response["msg"])

                elif response["type"] == "error":
                    print("[ERROR]", response["msg"])
                    break
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    client_main()
