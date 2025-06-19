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
    {"id": 3, "name": "Survivor", "desc": "Reach level 3", "type": "level", "goal": 3, "progress": 0, "completed": False, "reward": "Magic Scroll"},
]

def assign_quests(player):
    for quest in QUESTS:
        quest_copy = dict(quest)  # Make a copy
        if "progress" not in quest_copy:
            quest_copy["progress"] = 0
        if quest_copy not in player.quests:
            player.quests.append(quest_copy)

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
# Exploration System
# -------------------------------
def explore(player):
    print("\nYou venture into the wilds...")
    time.sleep(1)
    outcome = random.random()

    if outcome < 0.6:
        enemy_pool = [
            ("Goblin", 30, 5, 20), ("Skeleton", 40, 7, 25),
            ("Wolf", 35, 6, 22), ("Bat", 25, 4, 15),
            ("Orc", 50, 10, 30), ("Troll", 60, 12, 40),
            ("Giant", 70, 15, 50)
        ]
        enemies = [e for e in enemy_pool if player.level >= 3 or e[1] < 50]
        e = random.choice(enemies)
        enemy = Enemy(e[0], e[1], e[2], e[3], random.random() < 0.03)
        battle(player, enemy)
    elif outcome < 0.7:
        heal = random.randint(10, 30)
        player.hp = min(player.max_hp, player.hp + heal)
        print(f"You discover a hidden cache and regain {heal} HP!")
    elif outcome < 0.8:
        visit_city(player)
    else:
        print("The area is peaceful. You relax and enjoy the scenery.")

    input("\nPress Enter to return to the menu...")

# -------------------------------
# Stat Allocation
# -------------------------------
def allocate_stats(player):
    if player.stat_points <= 0:
        print("\nNo stat points to allocate.")
        return

    print(f"\nYou have {player.stat_points} stat points.")
    options = ["1. Max HP (+4)", "2. Attack (+1)"]
    if player.role == "Mage":
        options += ["3. Max Mana (+5)", "4. Spell Power (+1)"]
    print("\n" + "\n".join(options))

    while player.stat_points > 0:
        if player.role == "Mage":
            choice = input("Choose (1-4), or 'q' to quit: ").strip()
        else:
            choice = input("Choose (1-2), or 'q' to quit: ").strip()

        if choice == '1':
            player.max_hp += 4
            player.hp += 4
        elif choice == '2':
            player.attack += 1
        elif choice == '3' and player.role == "Mage":
            player.max_mana += 5
            player.mana += 5
        elif choice == '4' and player.role == "Mage":
            player.spell_power += 1
        elif choice == 'q':
            break
        else:
            print("Invalid choice.")
            continue

        player.stat_points -= 1
        print("Stat applied.")

    print("\nAllocation complete.")

# -------------------------------
# Battle System
# -------------------------------
def battle(player, enemy):
    print(f"\nA wild {enemy.name} appears! Prepare for battle!")
    bleed_turns = 0

    while enemy.hp > 0 and player.hp > 0:
        print(f"\n{player.name}: {player.hp} HP")
        if player.role == "Mage":
            print(f"Mana: {player.mana}/{player.max_mana}")
        print(f"{enemy.name}: {enemy.hp} HP")

        choice = input("Choose action: (1) Attack  (2) Use Inventory: ").strip()

        if choice == '1':
            if player.role == "Mage" and player.mana >= 10:
                spell_choice = input("Cast spell? (f) Fireball (-10 MP, +spell power) or (n) Normal Attack: ").strip().lower()
                if spell_choice == 'f':
                    damage = player.attack + player.spell_power
                    player.mana -= 10
                    print(f"You cast Fireball for {damage} damage!")
                else:
                    damage = player.attack
                    print(f"You attack the {enemy.name} for {damage} damage!")
            else:
                damage = player.attack
                print(f"You attack the {enemy.name} for {damage} damage!")

            if random.randint(1, 100) <= player.bleed_chance:
                bleed_turns = 3
                print("Bleed applied! Enemy will take damage for 3 turns.")

            enemy.hp -= damage
        elif choice == '2':
            manage_inventory(player)
            continue
        else:
            print("Invalid choice.")
            continue

        if enemy.hp > 0:
            enemy_damage = enemy.attack
            if enemy.has_bleed_enchantment and random.random() < 0.1:
                print("You are inflicted with bleed!")
                for _ in range(3):
                    player.hp -= 3
                    print("You bleed for 3 damage.")
            player.hp -= enemy_damage
            print(f"The {enemy.name} attacks for {enemy_damage} damage!")

        if bleed_turns > 0:
            enemy.hp -= 5
            print("Enemy suffers 5 bleed damage.")
            bleed_turns -= 1

    if player.hp > 0:
        print(f"\nYou defeated the {enemy.name}!")
        player.xp += enemy.xp_reward
        print(f"You gained {enemy.xp_reward} XP!")
        if player.xp >= player.level * 100:
            level_up(player)
        check_quests(player, "kill")

    else:
        print("\nYou have fallen in battle.")

# -------------------------------
# Level Up System
# -------------------------------
def level_up(player):
    player.level += 1
    player.stat_points += 3
    player.max_hp += 10
    player.hp = player.max_hp
    player.attack += 2
    if player.role == "Mage":
        player.max_mana += 10
        player.mana = player.max_mana
        player.spell_power += 2
    print(f"\n*** {player.name} leveled up to {player.level}! Stat points +3 ***")

def manage_inventory(player):
    if not player.inventory:
        print("\nYour inventory is empty.")
        input("Press Enter to continue...")
        return

    print("\n==== Inventory ====")
    for idx, item in enumerate(player.inventory, 1):
        print(f"{idx}. {item}")
    choice = input("Choose item to use (or Enter to cancel): ").strip()

# -------------------------------
# Save/Load Functions
# -------------------------------
def save_game(player):
    filename = input("Enter a name for your save file: ").strip() or "save_game"
    filepath = f"{filename}.json"

    if os.path.exists(filepath):
        confirm = input("A save with this name already exists. Overwrite? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Save cancelled.")
            return

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
