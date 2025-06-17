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

# -------------------------------
# (Rest of your existing code continues...)
