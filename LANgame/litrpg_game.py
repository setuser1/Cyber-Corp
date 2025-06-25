import random
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

    def to_dict(self):
        return self.__dict__

    def from_dict(self, data):
        self.__dict__.update(data)

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
]

def assign_quests(player):
    for q in QUESTS:
        quest = dict(q)
        if quest not in player.quests:
            player.quests.append(quest)

def check_quests(player, type_, value=1):
    logs = []
    for quest in player.quests:
        if quest["completed"]:
            continue
        if quest["type"] == type_:
            if type_ == "kill":
                quest["progress"] += value
            if quest["progress"] >= quest["goal"]:
                quest["completed"] = True
                player.inventory.append(quest["reward"])
                logs.append(f"{player.name} completed quest: {quest['name']} and received {quest['reward']}!")
    return logs

# -------------------------------
# Game Logic Functions
# -------------------------------
def level_up(player):
    player.level += 1
    player.stat_points += 3
    player.max_hp += 10
    player.hp = player.max_hp
    player.attack += 2
    logs = [f"{player.name} leveled up to {player.level}! Stat points +3"]
    if player.role == "Mage":
        player.max_mana += 10
        player.mana = player.max_mana
        player.spell_power += 2
        logs.append(f"{player.name}'s mana and spell power increased!")
    return logs

def explore(player, all_players):
    logs = [f"{player.name} ventures into the wilds..."]
    outcome = random.random()

    if outcome < 0.6:
        enemies = [
            ("Goblin", 30, 5, 20), ("Skeleton", 40, 7, 25),
            ("Wolf", 35, 6, 22), ("Bat", 25, 4, 15),
            ("Orc", 50, 10, 30), ("Troll", 60, 12, 40),
            ("Giant", 70, 15, 50)
        ]
        e = random.choice(enemies)
        enemy = Enemy(e[0], e[1], e[2], e[3], random.random() < 0.1)

        if len([p for p in all_players if p.hp > 0]) > 1:
            logs += group_battle(all_players, enemy)
        else:
            logs += battle(player, enemy)
    elif outcome < 0.75:
        heal = random.randint(10, 30)
        player.hp = min(player.max_hp, player.hp + heal)
        logs.append(f"{player.name} found a healing spring and restored {heal} HP!")
    elif outcome < 0.85:
        gold = random.randint(10, 20)
        player.gold += gold
        logs.append(f"{player.name} found an old chest and looted {gold} gold!")
    else:
        logs.append("Nothing eventful happens...")

    return logs

def battle(player, enemy):
    logs = [f"{player.name} encountered a {enemy.name}!"]
    bleed_turns = 0

    while enemy.hp > 0 and player.hp > 0:
        damage = player.attack
        if player.role == "Mage" and player.mana >= 10:
            damage += player.spell_power
            player.mana -= 10
            logs.append(f"{player.name} casts Fireball for {damage} damage!")
        else:
            logs.append(f"{player.name} attacks for {damage} damage!")

        enemy.hp -= damage

        if random.randint(1, 100) <= player.bleed_chance:
            bleed_turns = 3
            logs.append(f"{enemy.name} is bleeding!")

        if enemy.hp > 0:
            enemy_damage = enemy.attack
            player.hp -= enemy_damage
            logs.append(f"{enemy.name} attacks {player.name} for {enemy_damage} damage!")

        if bleed_turns > 0:
            enemy.hp -= 5
            logs.append(f"{enemy.name} suffers 5 bleed damage.")
            bleed_turns -= 1

    if player.hp > 0:
        logs.append(f"{player.name} defeated the {enemy.name}!")
        player.xp += enemy.xp_reward
        logs.append(f"{player.name} gained {enemy.xp_reward} XP.")
        if player.xp >= player.level * 100:
            logs += level_up(player)
        logs += check_quests(player, "kill")
    else:
        logs.append(f"{player.name} was defeated...")

    return logs

def group_battle(players, enemy):
    logs = [f"A group battle begins against {enemy.name}!"]
    bleed_turns = 0

    while enemy.hp > 0 and any(p.hp > 0 for p in players):
        for p in players:
            if p.hp <= 0:
                continue
            damage = p.attack
            if p.role == "Mage" and p.mana >= 10:
                damage += p.spell_power
                p.mana -= 10
                logs.append(f"{p.name} casts Fireball for {damage} damage!")
            else:
                logs.append(f"{p.name} attacks for {damage} damage!")
            enemy.hp -= damage
            if random.randint(1, 100) <= p.bleed_chance:
                bleed_turns = 3
                logs.append(f"{enemy.name} is bleeding!")
            if enemy.hp <= 0:
                break

        if enemy.hp > 0:
            target = random.choice([p for p in players if p.hp > 0])
            dmg = enemy.attack
            target.hp -= dmg
            logs.append(f"{enemy.name} hits {target.name} for {dmg} damage!")

            if enemy.has_bleed_enchantment and random.random() < 0.1:
                for _ in range(3):
                    target.hp -= 3
                    logs.append(f"{target.name} bleeds for 3 damage.")

            if bleed_turns > 0:
                enemy.hp -= 5
                logs.append(f"{enemy.name} suffers 5 bleed damage.")
                bleed_turns -= 1

    if enemy.hp <= 0:
        logs.append(f"The party has defeated {enemy.name}!")
        for p in players:
            if p.hp > 0:
                p.xp += enemy.xp_reward
                logs.append(f"{p.name} earned {enemy.xp_reward} XP!")
                if p.xp >= p.level * 100:
                    logs += level_up(p)
                logs += check_quests(p, "kill")
    else:
        logs.append("All players have fallen.")

    return logs

# -------------------------------
# Item System
# -------------------------------
def use_item(player, item, players):
    logs = []

    if item not in player.inventory:
        return [f"{item} not in inventory."]

    if item == "Health Potion":
        if player.hp < player.max_hp:
            heal = min(30, player.max_hp - player.hp)
            player.hp += heal
            logs.append(f"{player.name} used a Health Potion and restored {heal} HP.")
            player.inventory.remove(item)
        else:
            logs.append("HP is already full.")
    elif item == "Mana Potion" and player.role == "Mage":
        if player.mana < player.max_mana:
            regen = min(30, player.max_mana - player.mana)
            player.mana += regen
            logs.append(f"{player.name} used a Mana Potion and restored {regen} MP.")
            player.inventory.remove(item)
        else:
            logs.append("Mana is already full.")
    elif item == "Phoenix Feather":
        unconscious = [p for p in players if p != player and p.hp <= 0]
        if unconscious:
            target = unconscious[0]
            target.hp = target.max_hp // 2
            player.inventory.remove(item)
            logs.append(f"{player.name} used Phoenix Feather to revive {target.name} with {target.hp} HP.")
        else:
            logs.append("No unconscious teammates to revive.")
    else:
        logs.append(f"{item} has no use right now.")

    return logs
