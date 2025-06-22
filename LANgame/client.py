
import socket
import pickle

SERVER_IP = input("Enter server IP address: ").strip()
PORT = 65432

# Connect to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, PORT))

# Wait for server welcome/info
msg = pickle.loads(s.recv(4096))
print(f"[SERVER] {msg.get('msg')}")

# Create and send character data
name = input("Enter your name: ").strip()
role_input = input("Choose your class (1 = Warrior, 2 = Mage): ").strip()
role = "Mage" if role_input == "2" else "Warrior"

player_data = {
    "name": name,
    "role": role
}

s.sendall(pickle.dumps(player_data))

# Wait for game loop to begin
while True:
    data = pickle.loads(s.recv(4096))

    if data["type"] == "turn":
        print("\n===== Your Turn =====")
        print(f"Name: {data['player']['name']}  HP: {data['player']['hp']}/{data['player']['max_hp']}")
        print("1. Explore")
        print("2. Use Inventory")
        print("3. Quit")
        choice = input("Choose an action: ").strip()

        if choice == "1":
            s.sendall(pickle.dumps({"command": "explore"}))
        elif choice == "2":
            item = input("Enter item name to use: ").strip()
            s.sendall(pickle.dumps({"command": "use_item", "item": item}))
        elif choice == "3":
            s.sendall(pickle.dumps({"command": "quit"}))
            break
        else:
            print("Invalid choice.")
            continue

    elif data["type"] == "log":
        print("\n--- Game Update ---")
        for entry in data["log"]:
            print(entry)
    elif data["type"] == "info":
        print(f"[SERVER] {data['msg']}")
    elif data["type"] == "error":
        print(f"[ERROR] {data['msg']}")
        break

s.close()
