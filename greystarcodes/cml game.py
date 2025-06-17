# Cleaned and Organized Python LitRPG Game
import random
import json
import os
import time

# -------------------------------
# Player Class
# -------------------------------
class Player:
    def __init__(self, name, role="Warrior"):
        self.name = name
        self.role = role
        self.level = 1
        self.xp = 0
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.inventory = []
        self.stat_points = 0
        self.bleed_chance = 0
        self.quests = []


        if role == "Mage":
            self.max_mana = 50
            self.mana = 50
            self.spell_power = 10

    def show_status(self):
        print(f"\n==== {self.name}'s Status ====")
        print(f"Class: {self.role}")
        print(f"Level: {self.level}  XP: {self.xp}")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"Attack: {self.attack}")
        print(f"Stat Points: {self.stat_points}")
        print(f"Bleed Chance: {self.bleed_chance}%")
        if self.role == "Mage":
            print(f"Mana: {self.mana}/{self.max_mana}")
            print(f"Spell Power: {self.spell_power}")
        print("===========================")

# -------------------------------
# Enemy Class
# -------------------------------
class Enemy:
    def __init__(self, name, hp, attack, xp_reward, has_bleed_enchantment=False):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.xp_reward = xp_reward
        self.has_bleed_enchantment = has_bleed_enchantment


# -------------------------------
# Quests
# -------------------------------

QUESTS = [
    {"id": 1, "name": "First Blood", "desc": "Defeat 1 enemy", "type": "kill", "goal": 1, "progress": 0, "completed": False, "reward": "Health Potion"},
    {"id": 2, "name": "Hunter", "desc": "Defeat 5 enemies", "type": "kill", "goal": 5, "progress": 0, "completed": False, "reward": "Steel Sword"},
    {"id": 3, "name": "Survivor", "desc": "Reach level 3", "type": "level", "goal": 3, "completed": False, "reward": "Magic Scroll"},
]

def assign_quests(player):
    for quest in QUESTS:
        if quest not in player.quests:
            player.quests.append(dict(quest))  # deep copy

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
        status = "✔" if quest["completed"] else f"{quest.get('progress', 0)}/{quest['goal']}"
        print(f"{quest['name']} - {quest['desc']} ({status})")
    input("Press Enter to continue...")

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

# -------------------------------
# Save/Load Game
# -------------------------------
def save_game(player):
    save_data = {
        "name": player.name,
        "role": player.role,
        "level": player.level,
        "xp": player.xp,
        "xp_to_level": player.xp_to_level,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "attack": player.attack,
        "inventory": player.inventory,
        "stat_points": player.stat_points,
        "bleed_chance": player.bleed_chance
    }

    if player.role == "Mage":
        save_data.update({
            "mana": player.mana,
            "max_mana": player.max_mana,
            "spell_power": player.spell_power
        })

    filename = f"save_{player.name.lower()}.json"
    with open(filename, "w") as f:
        json.dump(save_data, f)
    print(f"\nGame saved successfully to {filename}!")


def load_game():
    saves = [f for f in os.listdir() if f.startswith("save_") and f.endswith(".json")]
    if not saves:
        print("No save files found.")
        return None

    print("\nAvailable Save Files:")
    for idx, file in enumerate(saves, 1):
        print(f"{idx}. {file}")

    try:
        choice = int(input("Enter the number of the save file to load: "))
        selected_file = saves[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None

    with open(selected_file, "r") as f:
        data = json.load(f)

    player = Player(
        name=data["name"],
        role=data["role"],
        level=data["level"],
        xp=data["xp"],
        xp_to_level=data["xp_to_level"],
        hp=data["hp"],
        max_hp=data["max_hp"],
        attack=data["attack"],
        inventory=data["inventory"],
        stat_points=data["stat_points"],
        bleed_chance=data["bleed_chance"],
        mana=data.get("mana", 0),
        max_mana=data.get("max_mana", 0),
        spell_power=data.get("spell_power", 0)
    )
    print(f"\nGame loaded successfully from {selected_file}!")
    return player


# -------------------------------
# City Visit (Placeholder)
# -------------------------------
def visit_city(player):
    print("\nYou arrive at a peaceful city. More features coming soon!")

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
# Inventory System
# -------------------------------
def manage_inventory(player):
    if not player.inventory:
        print("\nYour inventory is empty.")
        input("Press Enter to continue...")
        return

    print("\n==== Inventory ====")
    for idx, item in enumerate(player.inventory, 1):
        print(f"{idx}. {item}")
    choice = input("Choose item to use (or Enter to cancel): ").strip()

    if choice == "":
        return

    try:
        i = int(choice) - 1
        if i < 0 or i >= len(player.inventory):
            print("Invalid selection.")
            return
        item = player.inventory.pop(i)

        if item == "Health Potion":
            heal = min(30, player.max_hp - player.hp)
            player.hp += heal
            print(f"Restored {heal} HP.")
        elif item == "Mana Potion" and player.role == "Mage":
            restore = min(20, player.max_mana - player.mana)
            player.mana += restore
            print(f"Restored {restore} Mana.")
        elif item == "Magic Scroll":
            if player.role == "Mage":
                player.max_mana += 10
                player.mana += 10
            else:
                player.attack += 2
            print("Magic energy flows through you.")
        elif item == "Steel Sword":
            player.attack += 5
            print("Attack increased by 5.")
        elif item == "Bleed Enchantment":
            if player.bleed_chance < 25:
                player.bleed_chance = min(25, player.bleed_chance + 1)
                print(f"Bleed chance now {player.bleed_chance}%.")
            else:
                print("Bleed already at max.")
        else:
            print("The item had no effect.")

    except ValueError:
        print("Invalid input.")

    input("Press Enter to continue...")

# -------------------------------
# Main Game Loop
# -------------------------------
def main():
    print("========================================")
    print(" Welcome to the Python LitRPG Adventure!")
    print("========================================\n")

    role = "Mage" if input("Choose class: 1) Warrior 2) Mage: ").strip() == '2' else "Warrior"

    if os.path.isfile("save_game.json"):
        if input("Load existing save? (y/n): ").lower() == 'y':
            player = load_game()
            if player is None:
                name = input("Enter character name: ")
                player = Player(name, role)
        else:
            name = input("Enter character name: ")
            player = Player(name, role)
    else:
        name = input("Enter character name: ")
        player = Player(name, role)

    while player.hp > 0:
        if player.role == "Mage":
            player.mana = min(player.max_mana, player.mana + 5)
            print(f"(Mana regen +5) Mana: {player.mana}/{player.max_mana}")

        print("\nChoose an action:")
        print("1. Explore")
        print("2. Check Status")
        print("3. Use Inventory")
        print("4. Allocate Stats")
        print("5. Save Game")
        print("6. Quit Game")

        action = input("Enter choice: ").strip()

        if action == '1':
            explore(player)
        elif action == '2':
            player.show_status()
            input("Press Enter to continue...")
        elif action == '3':
            manage_inventory(player)
        elif action == '4':
            allocate_stats(player)
        elif action == '5':
            save_game(player)
        elif action == '6':
            print("\nThanks for playing!")
            break
        else:
            print("Invalid selection.")

    if player.hp <= 0:
        print("\nYou have died. Game Over.")

if __name__ == "__main__":
    main()
