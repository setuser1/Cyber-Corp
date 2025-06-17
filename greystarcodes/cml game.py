# -------------------------------
# Import and Initialization
# -------------------------------
import random
import json
import os
import time

# -------------------------------
# Player and Enemy Classes
# -------------------------------
class Player:
    def __init__(self, name, role="Warrior"):
        self.name = name
        self.role = role
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.xp = 0
        self.level = 1
        self.stat_points = 0
        self.inventory = []
        self.bleed_chance = 0
        self.skills = {}
        self.skill_cooldowns = {}
        if role == "Mage":
            self.max_mana = 50
            self.mana = 50
            self.spell_power = 10
        else:
            self.max_mana = 0
            self.mana = 0
            self.spell_power = 0
        self.learn_skills()

    def learn_skills(self):
        if self.role == "Warrior":
            self.skills = {
                "Power Strike": {"cooldown": 3, "current_cd": 0},
                "Defensive Stance": {"cooldown": 5, "current_cd": 0},
            }
        elif self.role == "Mage":
            self.skills = {
                "Fireball": {"cooldown": 2, "mana_cost": 15, "current_cd": 0},
                "Heal": {"cooldown": 3, "mana_cost": 10, "current_cd": 0},
            }

    def reduce_cooldowns(self):
        for skill in self.skills:
            if self.skills[skill]["current_cd"] > 0:
                self.skills[skill]["current_cd"] -= 1

    def show_status(self):
        print(f"\nName: {self.name}\nClass: {self.role}\nHP: {self.hp}/{self.max_hp}\nAttack: {self.attack}\nXP: {self.xp}\nLevel: {self.level}\nStat Points: {self.stat_points}")
        if self.role == "Mage":
            print(f"Mana: {self.mana}/{self.max_mana}\nSpell Power: {self.spell_power}")
        if self.bleed_chance:
            print(f"Weapon Bleed Chance: {self.bleed_chance}%")

class Enemy:
    def __init__(self, name, hp, attack, xp_reward, has_bleed_enchantment=False):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.xp_reward = xp_reward
        self.has_bleed_enchantment = has_bleed_enchantment

# -------------------------------
# Save and Load System
# -------------------------------
def save_game(player):
    data = player.__dict__.copy()
    with open("save_game.json", "w") as file:
        json.dump(data, file)
    print("Game saved successfully!")

def load_game():
    try:
        with open("save_game.json", "r") as file:
            data = json.load(file)
            player = Player(data["name"], data["role"])
            player.__dict__.update(data)
            return player
    except Exception as e:
        print("Failed to load game:", e)
        return None

# -------------------------------
# Skill Usage
# -------------------------------
def use_skill(player, enemy):
    print("\nSkills:")
    for i, skill in enumerate(player.skills.keys(), 1):
        info = player.skills[skill]
        cd = info["current_cd"]
        if player.role == "Mage":
            cost = info["mana_cost"]
            print(f"{i}. {skill} (CD: {cd}, Mana: {cost})")
        else:
            print(f"{i}. {skill} (CD: {cd})")
    print(f"{len(player.skills)+1}. Cancel")
    choice = input("Choose a skill: ").strip()
    try:
        choice = int(choice)
        if choice == len(player.skills) + 1:
            return False
        skill_name = list(player.skills.keys())[choice - 1]
        skill = player.skills[skill_name]

        if skill["current_cd"] > 0:
            print(f"{skill_name} is on cooldown!")
            return False

        if player.role == "Mage" and player.mana < skill["mana_cost"]:
            print("Not enough mana!")
            return False

        # Execute skill effect
        if player.role == "Warrior":
            if skill_name == "Power Strike":
                damage = player.attack + 10
                print(f"You use Power Strike and deal {damage} damage!")
                enemy.hp -= damage
            elif skill_name == "Defensive Stance":
                print("You brace yourself, reducing damage taken for the next 2 turns!")
                player.defending = 2
        elif player.role == "Mage":
            if skill_name == "Fireball":
                damage = player.spell_power * 2
                print(f"You cast Fireball and deal {damage} damage!")
                enemy.hp -= damage
                player.mana -= skill["mana_cost"]
            elif skill_name == "Heal":
                heal = 20
                actual_heal = min(heal, player.max_hp - player.hp)
                player.hp += actual_heal
                player.mana -= skill["mana_cost"]
                print(f"You heal for {actual_heal} HP!")

        player.skills[skill_name]["current_cd"] = player.skills[skill_name]["cooldown"]
        return True
    except (ValueError, IndexError):
        print("Invalid choice.")
        return False

# -------------------------------
# Battle System
# -------------------------------
def battle(player, enemy):
    print(f"\nA wild {enemy.name} appears!")
    defending = 0
    while player.hp > 0 and enemy.hp > 0:
        print(f"\n{player.name}: {player.hp}/{player.max_hp} HP")
        if player.role == "Mage":
            print(f"Mana: {player.mana}/{player.max_mana}")
        print(f"{enemy.name}: {enemy.hp} HP")
        print("\nChoose your action:")
        print("1. Attack")
        print("2. Use Skill")
        print("3. Use Inventory")
        choice = input("Action: ").strip()

        if choice == '1':
            damage = player.attack
            if random.randint(1, 100) <= player.bleed_chance:
                print("Your attack causes bleeding!")
                damage += 5
            print(f"You attack for {damage} damage!")
            enemy.hp -= damage
        elif choice == '2':
            if use_skill(player, enemy):
                pass
            else:
                continue
        elif choice == '3':
            manage_inventory(player)
            continue
        else:
            print("Invalid action.")
            continue

        if enemy.hp > 0:
            enemy_damage = enemy.attack
            if hasattr(player, 'defending') and player.defending > 0:
                enemy_damage = max(0, enemy_damage - 5)
                player.defending -= 1
            print(f"The {enemy.name} attacks you for {enemy_damage} damage!")
            player.hp -= enemy_damage

        player.reduce_cooldowns()

    if player.hp > 0:
        print(f"\nYou defeated the {enemy.name}!")
        player.xp += enemy.xp_reward
        print(f"You gain {enemy.xp_reward} XP!")
        level_up(player)
    else:
        print("\nYou were defeated...")

# -------------------------------
# Level Up Function
# -------------------------------
def level_up(player):
    xp_needed = player.level * 100
    if player.xp >= xp_needed:
        player.level += 1
        player.stat_points += 5
        player.hp = player.max_hp
        if player.role == "Mage":
            player.mana = player.max_mana
        print(f"\nYou leveled up to level {player.level}!")
        print("You gained 5 stat points!")

# This is the continuation and completion of your full LitRPG game code
# Assumes class definitions (Player, Enemy), and prior functions are defined

# -------------------------------
# Shop Function (Now a menu option)
# -------------------------------
def visit_shop(player):
    print("\n==== Welcome to the Shop ====")
    shop_items = [
        ("Health Potion", 10),
        ("Mana Potion", 15),
        ("Magic Scroll", 30),
        ("Steel Sword", 50),
        ("Bleed Enchantment", 75)
    ]
    for i, (item, cost) in enumerate(shop_items, 1):
        print(f"{i}. {item} - {cost} gold")
    print("0. Exit Shop")

    while True:
        print(f"\nGold: {player.gold}")
        choice = input("Enter the number of the item you wish to buy (0 to exit): ").strip()
        if choice == '0':
            break
        try:
            index = int(choice) - 1
            if index < 0 or index >= len(shop_items):
                print("Invalid choice.")
                continue
            item, cost = shop_items[index]
            if player.gold >= cost:
                player.gold -= cost
                player.inventory.append(item)
                print(f"You bought a {item}!")
            else:
                print("Not enough gold.")
        except ValueError:
            print("Invalid input.")

# -------------------------------
# Quest System
# -------------------------------
quest_list = [
    {
        "name": "Defeat 3 Goblins",
        "type": "kill",
        "target": "Goblin",
        "goal": 3,
        "progress": 0,
        "reward": 50
    },
    {
        "name": "Collect 2 Bleed Enchantments",
        "type": "collect",
        "target": "Bleed Enchantment",
        "goal": 2,
        "progress": 0,
        "reward": 75
    }
]

# Active quests will be stored in the player object as player.quests

def visit_quest_board(player):
    print("\n==== Quest Board ====")
    if not player.quests:
        available = [q for q in quest_list if q not in player.completed_quests]
        for i, quest in enumerate(available, 1):
            print(f"{i}. {quest['name']}")
        print("0. Exit")

        choice = input("Choose a quest to accept: ").strip()
        if choice == '0':
            return
        try:
            index = int(choice) - 1
            selected = available[index]
            player.quests.append(selected.copy())
            print(f"You accepted the quest: {selected['name']}")
        except:
            print("Invalid selection.")
    else:
        print("Current Quests:")
        for i, q in enumerate(player.quests, 1):
            print(f"{i}. {q['name']} ({q['progress']}/{q['goal']})")

# Call this function when an enemy is defeated or item collected

def update_quests(player, enemy_name=None, collected_item=None):
    for quest in player.quests[:]:
        if quest['type'] == 'kill' and enemy_name == quest['target']:
            quest['progress'] += 1
        elif quest['type'] == 'collect' and collected_item == quest['target']:
            quest['progress'] += 1

        if quest['progress'] >= quest['goal']:
            print(f"\nQuest Complete: {quest['name']}!")
            print(f"You received {quest['reward']} gold.")
            player.gold += quest['reward']
            player.completed_quests.append(quest)
            player.quests.remove(quest)

# Make sure Player class has:
# self.quests = []
# self.completed_quests = []
# self.gold = 0

# -------------------------------
# Add new options to main menu loop
# -------------------------------
# Replace the main game loop portion in your main() with this inside the while loop:

        print("\nWhat would you like to do next?")
        print("1. Explore")
        print("2. Check Status")
        print("3. Use Inventory")
        print("4. Allocate Stats")
        print("5. Save Game")
        print("6. Visit Shop")
        print("7. Quest Board")
        print("8. Quit Game")
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
            visit_shop(player)
        elif choice == '7':
            visit_quest_board(player)
        elif choice == '8':
            print("\nThanks for playing the Python LitRPG Adventure!")
            break
        else:
            print("\nInvalid selection. Please choose a number from the menu.")

# Don't forget to call update_quests(player, enemy_name=enemy.name) when an enemy is defeated
# and update_quests(player, collected_item=item_name) when using an inventory item

if __name__ == "__main__":
    main()
