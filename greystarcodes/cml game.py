#save delete function added
#exploration function updated to be compatible with multiple players

import os
import random
import json
import time
import datetime

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
def explore(current_player, all_players):
    print(f"\n{current_player.name} ventures into the wilds...")
    time.sleep(1)
    outcome = random.random()

    if outcome < 0.6:
        enemy_pool = [
            ("Goblin", 30, 5, 20), ("Skeleton", 40, 7, 25),
            ("Wolf", 35, 6, 22), ("Bat", 25, 4, 15),
            ("Orc", 50, 10, 30), ("Troll", 60, 12, 40),
            ("Giant", 70, 15, 50)
        ]
        enemies = [e for e in enemy_pool if current_player.level >= 3 or e[1] < 50]
        e = random.choice(enemies)
        enemy = Enemy(e[0], e[1], e[2], e[3], random.random() < 0.03)

        # Only trigger group battle if there are 2 or more *alive* players
        living_players = [p for p in all_players if p.hp > 0]
        if len(living_players) >= 2:
            group_battle(living_players, enemy)
        else:
            battle(current_player, enemy)

    elif outcome < 0.7:
        heal = random.randint(10, 30)
        current_player.hp = min(current_player.max_hp, current_player.hp + heal)
        print(f"You discover a hidden cache and regain {heal} HP!")
    elif outcome < 0.8:
        gold_found = random.randint(10, 20)
        current_player.gold += gold_found
        print(f"You discover an abandoned wagon with {gold_found} gold inside!")
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

def group_battle(players, enemy):
    print(f"\nA wild {enemy.name} appears! All players must fight together!")

    bleed_turns = 0
    while enemy.hp > 0 and any(p.hp > 0 for p in players):
        print(f"\n{enemy.name}: {enemy.hp} HP")
        for p in players:
            if p.hp <= 0:
                continue
            print(f"\n{p.name}: {p.hp} HP", end='')
            if p.role == "Mage":
                print(f", Mana: {p.mana}/{p.max_mana}")
            else:
                print()

            choice = input(f"{p.name}'s turn - (1) Attack  (2) Inventory: ").strip()
            if choice == '1':
                if p.role == "Mage" and p.mana >= 10:
                    spell_choice = input("Cast spell? (f) Fireball or (n) Normal Attack: ").strip().lower()
                    if spell_choice == 'f':
                        damage = p.attack + p.spell_power
                        p.mana -= 10
                        print(f"{p.name} casts Fireball for {damage} damage!")
                    else:
                        damage = p.attack
                        print(f"{p.name} attacks for {damage} damage!")
                else:
                    damage = p.attack
                    print(f"{p.name} attacks for {damage} damage!")

                if random.randint(1, 100) <= p.bleed_chance:
                    bleed_turns = 3
                    print("Bleed applied!")

                enemy.hp -= damage
            elif choice == '2':
                manage_inventory(p)

            if enemy.hp <= 0:
                break

        if enemy.hp > 0:
            target = random.choice([p for p in players if p.hp > 0])
            damage = enemy.attack
            target.hp -= damage
            print(f"\nThe {enemy.name} attacks {target.name} for {damage} damage!")

            if enemy.has_bleed_enchantment and random.random() < 0.1:
                print(f"{target.name} is bleeding!")
                for _ in range(3):
                    target.hp -= 3
                    print(f"{target.name} bleeds for 3 damage.")

            if bleed_turns > 0:
                enemy.hp -= 5
                print("Enemy suffers 5 bleed damage.")
                bleed_turns -= 1

    if enemy.hp <= 0:
        print(f"\nThe {enemy.name} is defeated!")
        for p in players:
            if p.hp > 0:
                p.xp += enemy.xp_reward
                print(f"{p.name} gains {enemy.xp_reward} XP!")
                if p.xp >= p.level * 100:
                    level_up(p)
                check_quests(p, "kill")
    else:
        print("\nThe party has been defeated.")

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
    choice = input("Choose item to use (or press Enter to cancel): ").strip()

    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(player.inventory):
        print("Cancelled or invalid choice.")
        return

    item = player.inventory[int(choice) - 1]

    # Item effects
    used = False
    if item == "Health Potion":
        if player.hp < player.max_hp:
            heal = min(30, player.max_hp - player.hp)
            player.hp += heal
            print(f"You used a Health Potion and restored {heal} HP!")
            used = True
        else:
            print("Your HP is already full.")
    elif item == "Mana Potion" and player.role == "Mage":
        if player.mana < player.max_mana:
            regen = min(30, player.max_mana - player.mana)
            player.mana += regen
            print(f"You used a Mana Potion and restored {regen} MP!")
            used = True
        else:
            print("Your Mana is already full.")
    elif item == "Magic Scroll" and player.role == "Mage":
        print("The Magic Scroll glows... You feel wiser!")
        player.spell_power += 1
        used = True
    elif item == "Steel Sword":
        print("You equip the Steel Sword. Attack +2!")
        player.attack += 2
        used = True
    elif item == "Bleed Enchantment":
        print("Your weapon gains a bleeding edge! Bleed chance +10%.")
        player.bleed_chance += 10
        used = True
    else:
        print(f"You can't use the {item} right now.")

    if used:
        player.inventory.pop(int(choice) - 1)

    input("Press Enter to continue...")

# -------------------------------
# Save/Load Functions
# -------------------------------
def save_multiplayer_game(players, filename="autosave", silent=False, timestamp=False, keep_latest=5):
    if timestamp:
        import datetime
        time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename_full = f"{filename}_{time_str}"
    else:
        filename_full = filename

    filepath = f"{filename_full}.json"

    with open(filepath, "w") as f:
        json.dump([p.__dict__ for p in players], f)

    if not silent:
        print(f"Game saved as {filepath}")

    # --- Limit autosaves to latest `keep_latest` files ---
    if timestamp:
        pattern = f"{filename}_"
        files = sorted(
            [f for f in os.listdir() if f.startswith(pattern) and f.endswith(".json")],
            key=os.path.getmtime,
            reverse=True
        )

        for old_file in files[keep_latest:]:
            os.remove(old_file)

def load_multiplayer_game():
    saves = [f for f in os.listdir() if f.endswith(".json")]
    if not saves:
        print("No save files found.")
        return []

    print("\nAvailable save files:")
    for idx, file in enumerate(saves):
        print(f"{idx + 1}. {file}")
    choice = input("Enter the number of the save to load: ").strip()

    try:
        filepath = saves[int(choice) - 1]
        with open(filepath, "r") as f:
            raw_players = json.load(f)

        players = []
        for pdata in raw_players:
            player = Player(pdata["name"], pdata.get("role", "Warrior"))
            player.__dict__.update(pdata)
            assign_quests(player)
            players.append(player)

        print(f"Loaded {len(players)} player(s).")
        return players
    except:
        print("Failed to load game.")
        return []

def cleanup_old_autosaves(base_name="autosave", keep_latest=1):
    files = sorted(
        [f for f in os.listdir() if f.startswith(base_name + "_") and f.endswith(".json")],
        key=os.path.getmtime,
        reverse=True
    )
    for old_file in files[keep_latest:]:
        try:
            os.remove(old_file)
            print(f"Deleted old autosave: {old_file}")
        except Exception as e:
            print(f"Failed to delete {old_file}: {e}")

def delete_save_file(protect_latest=True, base_name="autosave"):
    saves = [f for f in os.listdir() if f.endswith(".json")]
    if not saves:
        print("No save files to delete.")
        return

    # Identify the latest autosave (if protection is enabled)
    latest_autosave = None
    if protect_latest:
        autosaves = [f for f in saves if f.startswith(base_name + "_")]
        if autosaves:
            latest_autosave = max(autosaves, key=os.path.getmtime)

    while True:
        print("\n==== Delete Save Files ====")
        for idx, file in enumerate(saves, 1):
            tag = " (LATEST AUTOSAVE)" if protect_latest and file == latest_autosave else ""
            print(f"{idx}. {file}{tag}")
        print("a. Delete all (except latest autosave)" if protect_latest else "a. Delete all")
        print("q. Cancel")

        choice = input("Choose a save to delete (by number), 'a' to delete all, or 'q' to cancel: ").strip().lower()

        if choice == 'q':
            print("Cancelled.")
            return
        elif choice == 'a':
            confirm = input("Are you sure you want to delete all save files" +
                            (" except the latest autosave" if protect_latest else "") +
                            "? (y/n): ").strip().lower()
            if confirm == 'y':
                deleted = 0
                for file in saves:
                    if protect_latest and file == latest_autosave:
                        continue
                    try:
                        os.remove(file)
                        deleted += 1
                    except Exception as e:
                        print(f"Failed to delete {file}: {e}")
                print(f"Deleted {deleted} save file(s).")
            else:
                print("Bulk deletion cancelled.")
            return
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(saves):
                filename = saves[idx]
                if protect_latest and filename == latest_autosave:
                    print("⚠ You cannot delete the latest autosave.")
                    continue
                confirm = input(f"Are you sure you want to delete '{filename}'? (y/n): ").strip().lower()
                if confirm == 'y':
                    try:
                        os.remove(filename)
                        print(f"Deleted {filename}")
                        saves.remove(filename)
                        if filename == latest_autosave:
                            latest_autosave = None
                    except Exception as e:
                        print(f"Error deleting file: {e}")
                else:
                    print("Deletion cancelled.")
            else:
                print("Invalid selection.")
        else:
            print("Invalid input.")

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
# Main Menu
# -------------------------------

def main_menu(player, players):
    menu = [
        ("Explore", lambda p: explore(p, players)),
        ("Check Status", lambda p: (p.show_status(), input("Press Enter to continue..."))),
        ("Use Inventory", manage_inventory),
        ("Allocate Stats", allocate_stats),
        ("Save Game", lambda p: save_multiplayer_game(players)),
        ("Quit Game", lambda p: "quit"),
        ("View Quests", show_quests),
        ("Visit Shop", shop),
        ("Delete Save File", lambda p: delete_save_file())
    ]

    if len(players) >= 2:
        menu.append(("Trade with another player", lambda p: trade_items(p, players)))

    print(f"\n--- {player.name}'s Turn ---")
    for i, (label, _) in enumerate(menu, 1):
        print(f"{i}. {label}")

    choice = input(f"Choose an option (1-{len(menu)}): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(menu)):
        print("Invalid choice.")
        return None  # Turn will repeat

    label, action = menu[int(choice) - 1]
    result = action(player)
    return result

# -------------------------------
# Player Interaction
# -------------------------------

def trade_items(player, players):
    others = [p for p in players if p != player and p.hp > 0]
    if not others:
        print("No other players are available for trading.")
        return

    print("\nAvailable players to trade with:")
    for idx, p in enumerate(others, 1):
        print(f"{idx}. {p.name}")

    choice = input("Choose a player to trade with (or press Enter to cancel): ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(others):
        print("Cancelled.")
        return

    target = others[int(choice) - 1]
    if not player.inventory:
        print("You have nothing to trade.")
        return

    print("\nYour inventory:")
    for idx, item in enumerate(player.inventory, 1):
        print(f"{idx}. {item}")
    item_choice = input("Choose an item to give: ").strip()
    try:
        item = player.inventory.pop(int(item_choice) - 1)
        target.inventory.append(item)
        print(f"You gave {item} to {target.name}.")
    except:
        print("Invalid choice.")

# -------------------------------
# Main Game Loop
# -------------------------------
def main():
    print("========================================")
    print(" Welcome to the Python LitRPG Adventure!")
    print("========================================\n")

    players = []
    save_name = "autosave"  # Default

    # Check if there are any save files
    if any(f.endswith(".json") for f in os.listdir()):
        if input("A saved game was found. Load it? (y/n): ").strip().lower() == 'y':
            players = load_multiplayer_game()
            if players:
                save_name = input("Name this session for future saves: ").strip() or "autosave"

    # If no players were loaded, create new game
    if not players:
        num_players = input("How many players? (1-4): ").strip()
        try:
            num_players = max(1, min(4, int(num_players)))
        except:
            num_players = 1

        for i in range(num_players):
            role_choice = input(f"Player {i + 1}, choose your class: Enter 1 for Warrior or 2 for Mage (default is Warrior): ").strip()
            role = "Mage" if role_choice == "2" else "Warrior"
            name = input(f"Enter name for Player {i + 1}: ").strip()
            player = Player(name, role)
            assign_quests(player)
            players.append(player)

        save_name = input("Name your save file: ").strip() or "autosave"

    # Game loop starts here
    turn = 0
    while any(p.hp > 0 for p in players):
        player = players[turn]
        if player.hp <= 0:
            print(f"\n{player.name} is unconscious and skips their turn.")
            turn = (turn + 1) % len(players)
            continue

        if player.role == "Mage":
            player.mana = min(player.max_mana, player.mana + 5)
            print(f"\n({player.name}'s mana regenerates by 5. Mana: {player.mana}/{player.max_mana})")

        result = main_menu(player, players)

        if result == "quit":
            print("\nThanks for playing!")
            response = input("Do you want to delete all autosaves except the most recent one? (y/n): ").strip().lower()
            if response == 'y':
                cleanup_old_autosaves(base_name=save_name)
            break


        # 🔥 Auto-save to named file
        save_multiplayer_game(players, filename=save_name, silent=True, timestamp=True, keep_latest=5)

        turn = (turn + 1) % len(players)

    print("\nGame over! All players have fallen or quit.")

if __name__ == "__main__":
    main()
