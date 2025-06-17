import os
import random
import json
import time

# -------------------------------
# Player and Enemy Classes
# -------------------------------
class Player:
    def __init__(self, name, role="Warrior"):
        self.name = name
        self.role = role
        self.level = 1
        self.xp = 0
        self.gold = 100
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.stat_points = 0
        self.inventory = []
        self.bleed_chance = 0
        self.quests = []
        if role == "Mage":
            self.mana = 50
            self.max_mana = 50
            self.spell_power = 10

    def show_status(self):
        print(f"\nName: {self.name} ({self.role})\nLevel: {self.level}  XP: {self.xp}\nHP: {self.hp}/{self.max_hp}  Gold: {self.gold}")
        if self.role == "Mage":
            print(f"Mana: {self.mana}/{self.max_mana}  Spell Power: {self.spell_power}")
        print(f"Attack: {self.attack}  Bleed Chance: {self.bleed_chance}%\nInventory: {self.inventory if self.inventory else 'Empty'}")

class Enemy:
    def __init__(self, name, hp, attack, xp_reward, has_bleed_enchantment=False):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.xp_reward = xp_reward
        self.has_bleed_enchantment = has_bleed_enchantment

# -------------------------------
# Quest System
# -------------------------------
QUESTS = [
    {"id": 1, "name": "First Blood", "desc": "Defeat 1 enemy", "type": "kill", "goal": 1, "progress": 0, "completed": False, "reward": "Health Potion"},
    {"id": 2, "name": "Hunter", "desc": "Defeat 5 enemies", "type": "kill", "goal": 5, "progress": 0, "completed": False, "reward": "Steel Sword"},
    {"id": 3, "name": "Survivor", "desc": "Reach level 3", "type": "level", "goal": 3, "completed": False, "reward": "Magic Scroll"},
]

def assign_quests(player):
    for quest in QUESTS:
        if quest not in player.quests:
            player.quests.append(dict(quest))

def check_quests(player, type_, value=1):
    for quest in player.quests:
        if quest["completed"]:
            continue
        if quest["type"] == type_:
            if type_ == "kill":
                quest["progress"] += value
            elif type_ == "level" and player.level >= quest["goal"]:
                quest["progress"] = quest["goal"]
        if quest["progress"] >= quest["goal"]:
            quest["completed"] = True
            player.inventory.append(quest["reward"])
            print(f"\nQuest Complete: {quest['name']}! You received a {quest['reward']}!")

def show_quests(player):
    print("\n==== Quest Log ====")
    for quest in player.quests:
        status = "✓" if quest["completed"] else f"{quest.get('progress', 0)}/{quest['goal']}"
        print(f"{quest['name']} - {quest['desc']} ({status})")
    input("Press Enter to continue...")

# -------------------------------
# Save/Load Functions
# -------------------------------
def save_game(player):
    filename = input("Enter a name for your save file: ").strip() or "save_game"
    filepath = f"{filename}.json"
    with open(filepath, "w") as f:
        json.dump(player.__dict__, f)
    print("Game saved!")

def load_game():
    saves = [f for f in os.listdir() if f.endswith(".json")]
    if not saves:
        print("No save files found.")
        return None
    print("\nAvailable save files:")
    for idx, file in enumerate(saves):
        print(f"{idx + 1}. {file}")
    choice = input("Enter the number of the save to load: ").strip()
    try:
        filepath = saves[int(choice) - 1]
        with open(filepath, "r") as f:
            data = json.load(f)
            player = Player(data["name"], data.get("role", "Warrior"))
            player.__dict__.update(data)
            assign_quests(player)
            return player
    except:
        print("Failed to load game.")
        return None

# -------------------------------
# Shop Function
# -------------------------------
def shop(player):
    print("\n==== Welcome to the Shop ====")
    items_for_sale = {
        "Health Potion": 20,
        "Mana Potion": 25,
        "Magic Scroll": 40,
        "Steel Sword": 50,
        "Bleed Enchantment": 60
    }
    for idx, (item, price) in enumerate(items_for_sale.items(), start=1):
        print(f"{idx}. {item} - {price} gold")
    print("0. Leave Shop")

    choice = input("Choose an item to buy or 0 to exit: ").strip()
    if choice == "0":
        print("You leave the shop.")
        return
    try:
        idx = int(choice) - 1
        item = list(items_for_sale.keys())[idx]
        price = items_for_sale[item]
        if player.gold >= price:
            player.gold -= price
            player.inventory.append(item)
            print(f"You bought a {item}!")
        else:
            print("You don't have enough gold.")
    except:
        print("Invalid selection.")
    input("Press Enter to continue...")

# -------------------------------
# Main Game Loop
# -------------------------------
def main():
    print("========================================")
    print(" Welcome to the Python LitRPG Adventure!")
    print("========================================\n")

    role_choice = input("Choose your class: Enter 1 for Warrior or 2 for Mage (default is Warrior): ").strip()
    role = "Mage" if role_choice == "2" else "Warrior"

    player = None
    if any(f.endswith(".json") for f in os.listdir()):
        if input("A saved game was found. Load it? (y/n): ").lower() == 'y':
            player = load_game()

    if not player:
        name = input("Enter your character name: ").strip()
        player = Player(name, role)
        assign_quests(player)

    while player.hp > 0:
        if player.role == "Mage":
            player.mana = min(player.max_mana, player.mana + 5)
            print(f"(Mana regenerates by 5. Mana: {player.mana}/{player.max_mana})")

        print("\nWhat would you like to do next?")
        print("1. Explore")
        print("2. Check Status")
        print("3. Use Inventory")
        print("4. Allocate Stats")
        print("5. Save Game")
        print("6. Quit Game")
        print("7. View Quests")
        print("8. Visit Shop")
        choice = input("Choose an option (1-8): ").strip()

        if choice == '1':
            explore(player)
        elif choice == '2':
            player.show_status()
            input("Press Enter to continue...")
        elif choice == '3':
            manage_inventory(player)
        elif choice == '4':
            allocate_stats(player)
        elif choice == '5':
            save_game(player)
        elif choice == '6':
            print("\nThanks for playing!")
            break
        elif choice == '7':
            show_quests(player)
        elif choice == '8':
            shop(player)
        else:
            print("Invalid option.")

    if player.hp <= 0:
        print("\nYour journey has ended. Better luck next time!")

if __name__ == "__main__":
    main()
