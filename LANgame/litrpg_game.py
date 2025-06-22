# litrpg_game.py (LAN multiplayer logic port from original LitRPG)

import random
import time
from litrpg_game import Enemy

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

QUESTS = [
    {"id": 1, "name": "First Blood", "desc": "Defeat 1 enemy", "type": "kill", "goal": 1, "progress": 0, "completed": False, "reward": "Health Potion"},
    {"id": 2, "name": "Hunter", "desc": "Defeat 5 enemies", "type": "kill", "goal": 5, "progress": 0, "completed": False, "reward": "Steel Sword"},
    {"id": 3, "name": "Survivor", "desc": "Reach level 3", "type": "level", "goal": 3, "progress": 0, "completed": False, "reward": "Magic Scroll"},
]

def assign_quests(player):
    for quest in QUESTS:
        if quest not in player.quests:
            player.quests.append(dict(quest))

def check_quests(player, type_, value=1):
    log = []
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
            log.append(f"Quest Complete: {quest['name']}! You received a {quest['reward']}!")
    return log

def level_up(player):
    log = []
    player.level += 1
    player.stat_points += 3
    player.max_hp += 10
    player.hp = player.max_hp
    player.attack += 2
    if player.role == "Mage":
        player.max_mana += 10
        player.mana = player.max_mana
        player.spell_power += 2
    log.append(f"*** {player.name} leveled up to {player.level}! Stat points +3 ***")
    return log

def explore(player, players):
    log = []
    log.append(f"{player.name} ventures into the wilds...")

    outcome = random.random()

    if outcome < 0.6:
        enemy_pool = [
            ("Goblin", 30, 5, 20), ("Skeleton", 40, 7, 25),
            ("Wolf", 35, 6, 22), ("Bat", 25, 4, 15),
            ("Orc", 50, 10, 30), ("Troll", 60, 12, 40),
            ("Giant", 70, 15, 50)
        ]
        enemies = [e for e in enemy_pool if player.level >= 3 or e[1] < 50]
        name, hp, atk, xp = random.choice(enemies)
        enemy = Enemy(name, hp, atk, xp, has_bleed_enchantment=(random.random() < 0.05))

        # Group battle if 2 or more players are alive
        living = [p for p in players if p.hp > 0]
        if len(living) >= 2:
            log.append(f"A {enemy.name} appears and ambushes the group!")
            log += group_battle(living, enemy)
        else:
            log.append(f"A wild {enemy.name} appears!")
            log += battle(player, enemy)

    elif outcome < 0.75:
        heal = random.randint(10, 30)
        actual = min(player.max_hp - player.hp, heal)
        player.hp += actual
        log.append(f"{player.name} finds a healing spring and recovers {actual} HP!")
    elif outcome < 0.9:
        gold = random.randint(10, 20)
        player.gold += gold
        log.append(f"{player.name} discovers a hidden pouch with {gold} gold!")
    else:
        log.append(f"{player.name} enjoys a moment of peace. Nothing happens.")

    return log
def use_item(player, item, players):
    log = []
    if item not in player.inventory:
        log.append("Item not found in inventory.")
        return log

    if item == "Health Potion":
        if player.hp < player.max_hp:
            healed = min(30, player.max_hp - player.hp)
            player.hp += healed
            log.append(f"{player.name} used a Health Potion and healed {healed} HP!")
            player.inventory.remove(item)
        else:
            log.append("HP is already full.")

    elif item == "Mana Potion" and player.role == "Mage":
        if player.mana < player.max_mana:
            gain = min(30, player.max_mana - player.mana)
            player.mana += gain
            log.append(f"{player.name} regained {gain} mana.")
            player.inventory.remove(item)
        else:
            log.append("Mana is already full.")

    elif item == "Magic Scroll" and player.role == "Mage":
        player.spell_power += 1
        log.append(f"{player.name} used a Magic Scroll. Spell Power +1!")
        player.inventory.remove(item)

    elif item == "Steel Sword":
        player.attack += 2
        log.append(f"{player.name} equipped the Steel Sword. Attack +2!")
        player.inventory.remove(item)

    elif item == "Bleed Enchantment":
        player.bleed_chance += 10
        log.append(f"{player.name} added a bleed enchantment. Bleed chance +10%.")
        player.inventory.remove(item)

    elif item == "Phoenix Feather":
        for ally in players:
            if ally != player and ally.hp <= 0:
                ally.hp = ally.max_hp // 2
                player.inventory.remove(item)
                log.append(f"{player.name} revived {ally.name} with a Phoenix Feather!")
                break
        else:
            log.append("No ally to revive.")
    else:
        log.append(f"Cannot use {item} right now.")

    return log
