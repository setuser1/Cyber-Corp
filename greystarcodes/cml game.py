#command line game, litrpg
#ai generated

import random
import time

# -------------------------------
# Classes for Player and Enemy
# -------------------------------

class Player:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.max_hp = 100
        self.hp = self.max_hp
        self.xp = 0
        self.attack = 10
        self.inventory = []

    def level_up(self):
        # Every time XP reaches 100 or more, level up!
        while self.xp >= 100:
            self.level += 1
            self.xp -= 100
            self.max_hp += 20
            self.hp = self.max_hp  # Restore HP on level up
            self.attack += 5
            print(f"\n*** Congratulations {self.name}! You leveled up to Level {self.level}! ***")
            print(f"New stats - Max HP: {self.max_hp}, Attack: {self.attack}\n")
            time.sleep(1)

    def show_status(self):
        print("\n==== Player Status ====")
        print(f"Name: {self.name}")
        print(f"Level: {self.level}")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"XP: {self.xp}/100")
        print("Inventory:", self.inventory if self.inventory else "Empty")
        print("=======================\n")


class Enemy:
    def __init__(self, name, hp, attack, xp_reward):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.xp_reward = xp_reward

    def is_alive(self):
        return self.hp > 0

# -------------------------------
# Battle Function
# -------------------------------

def battle(player, enemy):
    print(f"\n*** A wild {enemy.name} appears! ***")
    time.sleep(1)
    while enemy.is_alive() and player.hp > 0:
        print(f"\n{player.name}'s HP: {player.hp}/{player.max_hp} | {enemy.name}'s HP: {enemy.hp}")
        action = input("Do you want to (a)ttack or (r)un? ").lower().strip()

        if action == 'a':
            # Player's turn
            damage = random.randint(max(1, player.attack // 2), player.attack)
            enemy.hp -= damage
            print(f"\nYou attack {enemy.name} for {damage} damage!")
            if not enemy.is_alive():
                print(f"\n*** You have defeated {enemy.name}! ***")
                player.xp += enemy.xp_reward
                print(f"You earned {enemy.xp_reward} XP!")
                player.level_up()
                # Chance to loot an item after winning
                if random.random() < 0.3:
                    item = random.choice(["Health Potion", "Magic Scroll", "Steel Sword"])
                    player.inventory.append(item)
                    print(f"You found a {item} on the enemy!")
                break  # Exit battle loop after enemy is defeated

            # Enemy's turn if still alive
            enemy_damage = random.randint(max(1, enemy.attack // 2), enemy.attack)
            player.hp -= enemy_damage
            print(f"{enemy.name} counterattacks for {enemy_damage} damage!")
            if player.hp <= 0:
                print("\n*** You have been defeated... Game Over! ***")
                break

        elif action == 'r':
            # Attempt to run away
            if random.random() > 0.5:
                print("\nYou successfully escaped the battle!")
                break
            else:
                print("\nYou failed to escape!")
                enemy_damage = random.randint(max(1, enemy.attack // 2), enemy.attack)
                player.hp -= enemy_damage
                print(f"As you try to run, {enemy.name} hits you for {enemy_damage} damage!")

        else:
            print("\nInvalid action. Please choose 'a' to attack or 'r' to run.")

        time.sleep(1)

    # Short pause after the battle
    input("\nPress Enter to continue...")

# -------------------------------
# Exploration Function
# -------------------------------

def explore(player):
    print("\nYou venture into the wilds...")
    time.sleep(1)
    outcome = random.random()
    if outcome < 0.6:
        # Encounter an enemy – different enemy types for variety
        enemy_types = [
            ("Goblin", 30, 5, 20),
            ("Skeleton", 40, 7, 25),
            ("Orc", 50, 10, 30),
        ]
        chosen_enemy = random.choice(enemy_types)
        enemy = Enemy(name=chosen_enemy[0], hp=chosen_enemy[1], attack=chosen_enemy[2], xp_reward=chosen_enemy[3])
        battle(player, enemy)
    else:
        # No enemy encountered – chance for a random rest or a simple treasure
        if outcome < 0.8:
            print("You discover a hidden cache of supplies and restore some health.")
            heal = random.randint(10, 30)
            player.hp = min(player.max_hp, player.hp + heal)
            print(f"You regained {heal} HP!")
        else:
            print("The area is peaceful, and you take the time to enjoy the scenery.")
    input("\nPress Enter to return to the menu...")

# -------------------------------
# Inventory Management Function
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
        
        # Define effects based on item type
        if item == "Health Potion":
            heal_amount = 30
            effective_heal = min(heal_amount, player.max_hp - player.hp)
            player.hp += effective_heal
            print(f"\nYou use a {item} and restore {effective_heal} HP!")
        elif item == "Magic Scroll":
            bonus = 2
            player.attack += bonus
            print(f"\nYou use a {item} and feel empowered! Your attack increases by {bonus} permanently.")
        elif item == "Steel Sword":
            bonus = 5
            player.attack += bonus
            print(f"\nYou wield the {item} expertly, increasing your attack by {bonus} permanently!")
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
    
    name = input("Enter your character name: ").strip()
    player = Player(name)
    
    while player.hp > 0:
        print("\nWhat would you like to do next?")
        print("1. Explore")
        print("2. Check Status")
        print("3. Use Inventory")
        print("4. Quit Game")
        choice = input("Choose an option (1-4): ").strip()

        if choice == '1':
            explore(player)
        elif choice == '2':
            player.show_status()
            input("Press Enter to continue...")
        elif choice == '3':
            manage_inventory(player)
        elif choice == '4':
            print("\nThanks for playing the Python LitRPG Adventure!")
            break
        else:
            print("\nInvalid selection. Please choose an option from the menu.")
    
    if player.hp <= 0:
        print("\nYour journey has ended. Better luck next time!")

# -------------------------------
# Run the Game
# -------------------------------

if __name__ == "__main__":
    main()
