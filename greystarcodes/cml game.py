import random
import time
import json
import os

# -------------------------------
# Classes for Player and Enemy
# -------------------------------
class Player:
    def __init__(self, name, role="Warrior"):
        self.name = name
        self.role = role  # "Warrior" or "Mage"
        self.level = 1
        self.max_hp = 100
        self.hp = self.max_hp
        self.xp = 0
        self.attack = 10
        self.inventory = []
        self.gold = 0                 # Player gold
        self.reputation = 100         # Player reputation (0-100)
        self.stat_points = 0          # Stat points available for allocation
        # For mage: add mana attributes; for Warrior, these remain 0.
        if self.role == "Mage":
            self.max_mana = 50
            self.mana = 50
        else:
            self.max_mana = 0
            self.mana = 0
        # Bleed chance and effects.
        self.bleed_chance = 0
        self.bleed_turns = 0
        self.bleed_damage = 0

    def level_up(self):
        # Each level up grants 5 stat points.
        while self.xp >= 100:
            self.level += 1
            self.xp -= 100
            self.stat_points += 5
            # Fully heal upon leveling up.
            self.hp = self.max_hp
            print(f"\n*** Congratulations {self.name}! You leveled up to Level {self.level}! ***")
            print("You have gained 5 stat points.")
            time.sleep(1)

    def show_status(self):
        print("\n==== Player Status ====")
        print(f"Name: {self.name} ({self.role})")
        print(f"Level: {self.level}")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"Attack: {self.attack}")
        if self.role == "Mage":
            print(f"Mana: {self.mana}/{self.max_mana}")
        print(f"XP: {self.xp}/100")
        print(f"Gold: {self.gold}")
        print(f"Reputation: {self.reputation}/100")
        print(f"Unallocated Stat Points: {self.stat_points}")
        print("Inventory:", self.inventory if self.inventory else "Empty")
        if self.bleed_chance > 0:
            print(f"Weapon Enchantment: Bleed (Chance: {self.bleed_chance}%)")
        print("=======================\n")

class Enemy:
    def __init__(self, name, hp, attack, xp_reward, has_bleed_enchantment=False):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.xp_reward = xp_reward
        self.has_bleed_enchantment = has_bleed_enchantment
        self.bleed_turns = 0
        self.bleed_damage = 0

    def is_alive(self):
        return self.hp > 0

# -------------------------------
# Save and Load Functions
# -------------------------------
def save_game(player):
    save_data = {
        "name": player.name,
        "role": player.role,
        "level": player.level,
        "max_hp": player.max_hp,
        "hp": player.hp,
        "xp": player.xp,
        "attack": player.attack,
        "inventory": player.inventory,
        "gold": player.gold,
        "reputation": player.reputation,
        "stat_points": player.stat_points,
        "max_mana": player.max_mana,
        "mana": player.mana,
        "bleed_chance": player.bleed_chance,
        "bleed_turns": player.bleed_turns,
        "bleed_damage": player.bleed_damage
    }
    with open("save_game.json", "w") as f:
        json.dump(save_data, f)
    print("\n--- Game saved! ---\n")

def load_game():
    try:
        with open("save_game.json", "r") as f:
            save_data = json.load(f)
        player = Player(save_data["name"], role=save_data.get("role", "Warrior"))
        player.level = save_data["level"]
        player.max_hp = save_data["max_hp"]
        player.hp = save_data["hp"]
        player.xp = save_data["xp"]
        player.attack = save_data["attack"]
        player.inventory = save_data["inventory"]
        player.gold = save_data["gold"]
        player.reputation = save_data["reputation"]
        player.stat_points = save_data["stat_points"]
        player.max_mana = save_data.get("max_mana", 0)
        player.mana = save_data.get("mana", 0)
        player.bleed_chance = save_data["bleed_chance"]
        player.bleed_turns = save_data["bleed_turns"]
        player.bleed_damage = save_data["bleed_damage"]
        print("\n--- Game loaded successfully! ---\n")
        return player
    except FileNotFoundError:
        print("\nNo saved game found.\n")
        return None

# -------------------------------
# Jail and Guard Battle Functions
# -------------------------------
def jail(player):
    print("\n*** You have been caught by the guards and are sent to jail! ***")
    lost_gold = int(player.gold * 0.3)
    player.gold -= lost_gold
    if player.inventory:
        lost_item = random.choice(player.inventory)
        player.inventory.remove(lost_item)
        print(f"In jail, they confiscated your {lost_item}!")
    healed_hp = int(0.3 * player.max_hp)
    player.hp = healed_hp
    print(f"Your HP is restored to {healed_hp} (30% of max). You lost {lost_gold} gold coins as a fine.")

def guard_battle(player, guard):
    print("\n*** You are now fighting a guard! ***")
    while guard.is_alive() and player.hp > 0:
        if player.bleed_turns > 0:
            print(f"\n{player.name} suffers {player.bleed_damage} bleed damage.")
            player.hp -= player.bleed_damage
            player.bleed_turns -= 1
            if player.hp <= 0:
                jail(player)
                return False
        if guard.bleed_turns > 0:
            print(f"\n{guard.name} suffers {guard.bleed_damage} bleed damage.")
            guard.hp -= guard.bleed_damage
            guard.bleed_turns -= 1
            if guard.hp <= 0:
                print(f"\n*** {guard.name} bled out and is defeated! ***")
                return True
        print(f"\n{player.name}'s HP: {player.hp}/{player.max_hp} | {guard.name}'s HP: {guard.hp}")
        action = input("Do you want to (a)ttack, (r)un, or access (i)nventory? ").lower().strip()
        if action == 'a':
            if player.hp <= player.max_hp * 0.3:
                effective_attack = max(1, player.attack - 3)
                print("\n[Debuff Active: Your low HP is reducing your attack by 3 points!]")
            else:
                effective_attack = player.attack
            damage = random.randint(max(1, effective_attack // 2), effective_attack)
            guard.hp -= damage
            print(f"\nYou attack the guard for {damage} damage!")
            if guard.hp <= 0:
                print("\n*** You have defeated the guard! ***")
                return True
            enemy_damage = random.randint(max(1, guard.attack // 2), guard.attack)
            player.hp -= enemy_damage
            print(f"\nThe guard counterattacks for {enemy_damage} damage!")
            if player.hp <= 0:
                jail(player)
                return False
        elif action == 'r':
            if random.random() > 0.5:
                print("\nYou managed to escape the guard!")
                return True
            else:
                print("\nYou failed to escape!")
                enemy_damage = random.randint(max(1, guard.attack // 2), guard.attack)
                player.hp -= enemy_damage
                print(f"\nThe guard hits you for {enemy_damage} damage!")
                if player.hp <= 0:
                    jail(player)
                    return False
        elif action == 'i':
            battle_inventory(player)
        else:
            print("\nInvalid selection. Choose 'a', 'r', or 'i'.")
        time.sleep(1)
    return True

def guard_encounter(player):
    print("\nGuards have caught you!")
    if player.hp < 0.2 * player.max_hp:
        print("Your HP is too low to fight the guards. They arrest you and send you straight to jail.")
        jail(player)
    else:
        print("You are strong enough to fight the guards!")
        guard = Enemy("Guard", hp=40, attack=8, xp_reward=0, has_bleed_enchantment=False)
        result = guard_battle(player, guard)
        if not result:
            return
        else:
            print("After the fight, your reputation suffers further!")
            player.reputation -= 10
            if player.reputation < 0:
                player.reputation = 0

# -------------------------------
# Mage Spell Casting Function
# -------------------------------
def mage_cast_spell(player, enemy):
    print("\n*** Spell Casting ***")
    print("Available spells:")
    print("1. Fireball (Cost: 10 mana) - Deals heavy damage.")
    print("2. Ice Blast (Cost: 5 mana) - Deals moderate damage.")
    spell_choice = input("Choose your spell (1 or 2): ").strip()
    if spell_choice == "1":
        if player.mana < 10:
            print("Not enough mana to cast Fireball!")
            return False
        player.mana -= 10
        damage = random.randint((player.attack // 2) + 10, player.attack + 10)
        enemy.hp -= damage
        print(f"You cast Fireball for {damage} damage!")
        return False  # Enemy may counterattack as usual.
    elif spell_choice == "2":
        if player.mana < 5:
            print("Not enough mana to cast Ice Blast!")
            return False
        player.mana -= 5
        damage = random.randint(3, 7)
        enemy.hp -= damage
        print(f"You cast Ice Blast for {damage} damage!")
        print("The enemy is chilled!")
        return False  # Unlike before, Ice Blast no longer prevents a counterattack.
    else:
        print("Invalid spell selection.")
        return False

# -------------------------------
# In-Battle Inventory Function
# -------------------------------
def battle_inventory(player):
    if not player.inventory:
        print("\nYour inventory is empty.")
        return
    print("\n==== Battle Inventory ====")
    for index, item in enumerate(player.inventory, start=1):
        print(f"{index}. {item}")
    choice = input("\nEnter the number of the item to use (or press Enter to cancel): ").strip()
    if choice == "":
        print("Canceled inventory usage.")
        return
    try:
        item_index = int(choice) - 1
        if item_index < 0 or item_index >= len(player.inventory):
            print("Invalid selection.")
            return
        item = player.inventory.pop(item_index)
        if random.random() < 0.05:
            print(f"\nIn the chaos of battle, you accidentally drop your {item}!")
            if random.random() < 0.03:
                player.inventory.append(item)
                print(f"Luckily, you quickly recover your {item}!")
            else:
                print(f"You lose your {item} and it is gone!")
            return
        if item == "Health Potion":
            heal_amount = 30
            effective_heal = min(heal_amount, player.max_hp - player.hp)
            player.hp += effective_heal
            print(f"\nYou use a {item} and restore {effective_heal} HP!")
        elif item == "Magic Scroll":
            if player.role == "Mage":
                bonus = 10
                player.max_mana += bonus
                player.mana += bonus
                print(f"\nYou use a {item} and your mana increases by {bonus} permanently!")
            else:
                bonus = 2
                player.attack += bonus
                print(f"\nYou use a {item} and feel empowered! Your attack increases by {bonus} permanently.")
        elif item == "Steel Sword":
            bonus = 5
            player.attack += bonus
            print(f"\nYou wield the {item} expertly, increasing your attack by {bonus} permanently!")
        elif item == "Bleed Enchantment":
            if player.bleed_chance == 0:
                player.bleed_chance = 10
                print("\nYour weapon is now imbued with a bleed enchantment! (Bleed chance: 10%)")
            else:
                if player.bleed_chance < 25:
                    player.bleed_chance += 1
                    print(f"\nYour weapon's bleed chance increases by 1%. (Bleed chance: {player.bleed_chance}%)")
                else:
                    print("\nYour weapon's bleed chance is already at its maximum (25%).")
        else:
            print(f"\nThe {item} had no effect when used.")
    except ValueError:
        print("Invalid selection.")

# -------------------------------
# Shop Interface with Limited Stock and Reputation-Based Prices
# -------------------------------
def shop_interface(player):
    shop_inventory = {
        "Health Potion": 10,
        "Magic Scroll": 15,
        "Steel Sword": 20,
        "Bleed Enchantment": 25
    }
    shop_stock = {
        "Health Potion": 3,
        "Magic Scroll": 2,
        "Steel Sword": 1,
        "Bleed Enchantment": 1
    }
    # Adjusted price formula: adjusted_price = base_price * (1 + ((100 - current_reputation) / 5))
    adjusted_prices = {item: int(price * (1 + ((100 - player.reputation) / 5)))
                       for item, price in shop_inventory.items()}
    print("\n--- Welcome to the Shop ---")
    print("Prices are adjusted based on your reputation.")
    print("Formula: adjusted_price = base_price * (1 + ((100 - current_reputation) / 5))")
    while True:
        print(f"\nYou have {player.gold} gold coins and your reputation is {player.reputation}/100.")
        print("Items available:")
        for item in shop_inventory:
            stock = shop_stock[item]
            price = adjusted_prices[item]
            print(f" - {item}: {price} gold (Stock: {stock})")
        print("Type the name of the item to purchase it,")
        print("or type 'steal <item>' to attempt to steal it,")
        print("or type 'exit' to leave the shop.")
        choice = input("Your choice: ").strip()
        if choice.lower() == "exit":
            print("You leave the shop and head back out into the world.")
            break
        elif choice.startswith("steal "):
            item_to_steal = choice[6:]
            if item_to_steal in shop_inventory:
                if shop_stock[item_to_steal] <= 0:
                    print(f"Sorry, there is no stock left of {item_to_steal} to steal.")
                else:
                    attempt_steal(player, item_to_steal, adjusted_prices[item_to_steal], shop_stock)
            else:
                print("That item is not available to steal.")
        elif choice in shop_inventory:
            if shop_stock[choice] <= 0:
                print("That item is out of stock.")
                continue
            price = adjusted_prices[choice]
            if player.gold >= price:
                player.gold -= price
                player.inventory.append(choice)
                shop_stock[choice] -= 1
                print(f"You purchased a {choice} for {price} gold!")
            else:
                print("You do not have enough gold for that item.")
        else:
            print("That item is not available.")

def attempt_steal(player, item, price, stock):
    print(f"\nYou attempt to steal a {item} from the shop!")
    if stock[item] <= 0:
        print("That item is out of stock and cannot be stolen.")
        return
    if random.random() < 0.3:
        print(f"You successfully stole a {item}!")
        player.inventory.append(item)
        stock[item] -= 1
    else:
        print(f"You failed to steal the {item}!")
        player.reputation -= 15
        if player.reputation < 0:
            player.reputation = 0
        if random.random() < 0.5:
            guard_encounter(player)
        else:
            print("Luckily, no guards were alerted this time.")

def visit_city(player):
    print("\nYou arrive at a bustling city full of merchants and adventurers.")
    time.sleep(1)
    shop_interface(player)
    input("\nPress Enter to leave the city and return to your adventure...")

# -------------------------------
# Standard Battle Function
# -------------------------------
def battle(player, enemy):
    print(f"\n*** A wild {enemy.name} appears! ***")
    time.sleep(1)
    while enemy.is_alive() and player.hp > 0:
        if player.bleed_turns > 0:
            print(f"\n{player.name} suffers {player.bleed_damage} bleed damage.")
            player.hp -= player.bleed_damage
            player.bleed_turns -= 1
            if player.hp <= 0:
                print("\n*** You have bled out... Game Over! ***")
                break
        if enemy.bleed_turns > 0:
            print(f"\n{enemy.name} suffers {enemy.bleed_damage} bleed damage.")
            enemy.hp -= enemy.bleed_damage
            enemy.bleed_turns -= 1
            if enemy.hp <= 0:
                print(f"\n*** {enemy.name} bled out and is defeated! ***")
                player.xp += enemy.xp_reward
                print(f"You earned {enemy.xp_reward} XP!")
                player.level_up()
                if random.random() < 0.3:
                    item = random.choice(["Health Potion", "Magic Scroll", "Steel Sword", "Bleed Enchantment"])
                    player.inventory.append(item)
                    print(f"You found a {item} on the enemy!")
                if random.random() < 0.20:
                    coins = random.randint(5, 15)
                    player.gold += coins
                    print(f"{enemy.name} dropped {coins} gold coins!")
                break
        if player.hp <= 0 or enemy.hp <= 0:
            break

        print(f"\n{player.name}'s HP: {player.hp}/{player.max_hp} | {enemy.name}'s HP: {enemy.hp}")
        if player.role == "Mage":
            prompt = "Do you want to (a)ttack, (r)un, (i)nventory, or cast a (s)pell? "
        else:
            prompt = "Do you want to (a)ttack, (r)un, or access (i)nventory? "
        action = input(prompt).lower().strip()
        if action == 's' and player.role == "Mage":
            skip_counter = mage_cast_spell(player, enemy)
            if enemy.hp <= 0:
                print(f"\n*** You have defeated {enemy.name} with your spell! ***")
                player.xp += enemy.xp_reward
                print(f"You earned {enemy.xp_reward} XP!")
                player.level_up()
                if random.random() < 0.3:
                    item = random.choice(["Health Potion", "Magic Scroll", "Steel Sword", "Bleed Enchantment"])
                    player.inventory.append(item)
                    print(f"You found a {item} on the enemy!")
                if random.random() < 0.20:
                    coins = random.randint(5, 15)
                    player.gold += coins
                    print(f"{enemy.name} dropped {coins} gold coins!")
                continue
        elif action == 'a':
            if player.hp <= player.max_hp * 0.3:
                effective_attack = max(1, player.attack - 3)
                print("\n[Debuff Active: Your low HP is reducing your attack by 3 points!]")
            else:
                effective_attack = player.attack
            damage = random.randint(max(1, effective_attack // 2), effective_attack)
            enemy.hp -= damage
            print(f"\nYou attack {enemy.name} for {damage} damage!")
            if not enemy.is_alive():
                print(f"\n*** You have defeated {enemy.name}! ***")
                player.xp += enemy.xp_reward
                print(f"You earned {enemy.xp_reward} XP!")
                player.level_up()
                if random.random() < 0.3:
                    item = random.choice(["Health Potion", "Magic Scroll", "Steel Sword", "Bleed Enchantment"])
                    player.inventory.append(item)
                    print(f"You found a {item} on the enemy!")
                if random.random() < 0.20:
                    coins = random.randint(5, 15)
                    player.gold += coins
                    print(f"{enemy.name} dropped {coins} gold coins!")
                break
            if player.bleed_chance > 0:
                if random.random() < (player.bleed_chance / 100):
                    enemy.bleed_turns = 3
                    enemy.bleed_damage = 5
                    print(f"{enemy.name} is now bleeding!")
        elif action == 'r':
            if random.random() > 0.5:
                print("\nYou successfully escaped the battle!")
                break
            else:
                print("\nYou failed to escape!")
                enemy_damage = random.randint(max(1, enemy.attack // 2), enemy.attack)
                player.hp -= enemy_damage
                print(f"As you try to run, {enemy.name} hits you for {enemy_damage} damage!")
        elif action == 'i':
            battle_inventory(player)
        else:
            print("\nInvalid selection. Please choose a valid option.")
        if enemy.is_alive() and action in ['a', 'i', 's']:
            if player.role == "Mage" and action == 's' and skip_counter:
                pass
            else:
                enemy_damage = random.randint(max(1, enemy.attack // 2), enemy.attack)
                player.hp -= enemy_damage
                print(f"\n{enemy.name} counterattacks for {enemy_damage} damage!")
                if enemy.has_bleed_enchantment:
                    if random.random() < 0.10:
                        player.bleed_turns = 3
                        player.bleed_damage = 5
                        print(f"{player.name} is now bleeding!")
                if player.hp <= 0:
                    print("\n*** You have been defeated... Game Over! ***")
                    break
        time.sleep(1)
    input("\nPress Enter to continue...")

# -------------------------------
# Exploration Function
# -------------------------------
def explore(player):
    print("\nYou venture into the wilds...")
    time.sleep(1)
    outcome = random.random()
    if outcome < 0.6:
        enemy_pool = [
            ("Goblin", 30, 5, 20),
            ("Skeleton", 40, 7, 25),
            ("Wolf", 35, 6, 22),
            ("Bat", 25, 4, 15),
            ("Orc", 50, 10, 30),
            ("Troll", 60, 12, 40),
            ("Giant", 70, 15, 50)
        ]
        if player.level < 3:
            enemy_types = [e for e in enemy_pool if e[1] < 50]
        else:
            enemy_types = enemy_pool
        chosen_enemy = random.choice(enemy_types)
        enemy = Enemy(
            name=chosen_enemy[0],
            hp=chosen_enemy[1],
            attack=chosen_enemy[2],
            xp_reward=chosen_enemy[3],
            has_bleed_enchantment=(random.random() < 0.03)
        )
        battle(player, enemy)
    else:
        if outcome < 0.7:
            print("You discover a small hidden cache of supplies and restore some health.")
            heal = random.randint(10, 30)
            player.hp = min(player.max_hp, player.hp + heal)
            print(f"You regained {heal} HP!")
        elif outcome < 0.8:
            visit_city(player)
        else:
            print("The area is peaceful, and you take the time to enjoy the scenery.")
    input("\nPress Enter to return to the menu...")

# -------------------------------
# Allocate Stat Points Function
# -------------------------------
def allocate_stats(player):
    if player.stat_points <= 0:
        print("\nYou have no stat points to allocate.")
        return
    print(f"\nYou have {player.stat_points} stat points to allocate.")
    print("1. Increase max HP by 4 per point")
    print("2. Increase Attack by 1 per point")
    if player.role == "Mage":
        print("3. Increase max Mana by 5 per point")
    while player.stat_points > 0:
        print(f"\nRemaining stat points: {player.stat_points}")
        if player.role == "Mage":
            choice = input("Enter 1 for HP, 2 for Attack, 3 for Mana, or 'q' to quit allocation: ").strip().lower()
        else:
            choice = input("Enter 1 for HP, 2 for Attack, or 'q' to quit allocation: ").strip().lower()
        if choice == '1':
            player.max_hp += 4
            player.hp += 4
            player.stat_points -= 1
            print("Increased max HP by 4.")
        elif choice == '2':
            player.attack += 1
            player.stat_points -= 1
            print("Increased Attack by 1.")
        elif choice == '3' and player.role == "Mage":
            player.max_mana += 5
            player.mana += 5
            player.stat_points -= 1
            print("Increased max Mana by 5.")
        elif choice == 'q':
            break
        else:
            print("Invalid selection. Please choose a valid option.")
    print("Allocation complete.")

# -------------------------------
# Inventory Management Function (Out of Battle)
# -------------------------------
def manage_inventory(player):
    if not player.inventory:
        print("\nYour inventory is empty.")
        input("Press Enter to continue...")
        return
    print("\n==== Inventory ====")
    for index, item in enumerate(player.inventory, start=1):
        print(f"{index}. {item}")
    choice = input("\nEnter the number of the item you want to use (or press Enter to cancel): ").strip()
    if choice == "":
        print("Canceled inventory usage.")
        input("Press Enter to continue...")
        return
    try:
        item_index = int(choice) - 1
        if item_index < 0 or item_index >= len(player.inventory):
            print("Invalid selection.")
            input("Press Enter to continue...")
            return
        item = player.inventory.pop(item_index)
        if item == "Health Potion":
            heal_amount = 30
            effective_heal = min(heal_amount, player.max_hp - player.hp)
            player.hp += effective_heal
            print(f"\nYou use a {item} and restore {effective_heal} HP!")
        elif item == "Magic Scroll":
            if player.role == "Mage":
                bonus = 10
                player.max_mana += bonus
                player.mana += bonus
                print(f"\nYou use a {item} and your mana increases by {bonus} permanently!")
            else:
                bonus = 2
                player.attack += bonus
                print(f"\nYou use a {item} and feel empowered! Your attack increases by {bonus} permanently.")
        elif item == "Steel Sword":
            bonus = 5
            player.attack += bonus
            print(f"\nYou wield the {item} expertly, increasing your attack by {bonus} permanently!")
        elif item == "Bleed Enchantment":
            if player.bleed_chance == 0:
                player.bleed_chance = 10
                print("\nYour weapon is now imbued with a bleed enchantment! (Bleed chance: 10%)")
            else:
                if player.bleed_chance < 25:
                    player.bleed_chance += 1
                    print(f"\nYour weapon's bleed chance increases by 1%. (Bleed chance: {player.bleed_chance}%)")
                else:
                    print("\nYour weapon's bleed chance is already at its maximum (25%).")
        else:
            print(f"\nThe {item} had no effect when used.")
    except ValueError:
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
    if role_choice == "2":
        role = "Mage"
    else:
        role = "Warrior"
        
    if os.path.isfile("save_game.json"):
        load_choice = input("A saved game was found. Would you like to load it? (y/n): ").strip().lower()
        if load_choice == 'y':
            player = load_game()
            if player is None:
                name = input("Enter your character name: ").strip()
                player = Player(name, role=role)
        else:
            name = input("Enter your character name: ").strip()
            player = Player(name, role=role)
    else:
        name = input("Enter your character name: ").strip()
        player = Player(name, role=role)
    
    while player.hp > 0:
        print("\nWhat would you like to do next?")
        print("1. Explore")
        print("2. Check Status")
        print("3. Use Inventory")
        print("4. Allocate Stats")
        print("5. Save Game")
        print("6. Quit Game")
        choice = input("Choose an option (1-6): ").strip()
        
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
            print("\nThanks for playing the Python LitRPG Adventure!")
            break
        else:
            print("\nInvalid selection. Please choose a number from the menu.")
    if player.hp <= 0:
        print("\nYour journey has ended. Better luck next time!")

if __name__ == "__main__":
    main()
