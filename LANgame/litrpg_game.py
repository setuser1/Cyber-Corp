# litrpg_game.py (LAN multiplayer logic port from original LitRPG)

import random
import time

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

def explore(player):
    log = [f"{player.name} explores the area..."]
    outcome = random.random()
    
    if outcome < 0.6:
        enemies = [
            ("Goblin", 30, 5, 20), ("Skeleton", 40, 7, 25),
            ("Wolf", 35, 6, 22), ("Bat", 25, 4, 15),
            ("Orc", 50, 10, 30), ("Troll", 60, 12, 40),
            ("Giant", 70, 15, 50)
        ]
        valid = [e for e in enemies if player.level >= 3 or e[1] < 50]
        name, hp, atk, xp = random.choice(valid)
        enemy = {"name": name, "hp": hp, "atk": atk, "xp": xp}

        # simplified single round battle
        damage = player.attack + (player.spell_power if player.role == "Mage" else 0)
        enemy["hp"] -= damage
        log.append(f"You attack the {enemy['name']} for {damage} damage!")

        if enemy["hp"] > 0:
            player.hp -= enemy["atk"]
            log.append(f"The {enemy['name']} strikes back for {enemy['atk']} damage!")

        if player.hp > 0:
            player.xp += enemy["xp"]
            log.append(f"You defeated the {enemy['name']} and gained {enemy['xp']} XP!")
            if player.xp >= player.level * 100:
                log += level_up(player)
            log += check_quests(player, "kill")
        else:
            log.append("You were defeated in battle!")

    elif outcome < 0.7:
        heal = random.randint(10, 30)
        player.hp = min(player.max_hp, player.hp + heal)
        log.append(f"You find a stream and regain {heal} HP.")
    elif outcome < 0.8:
        gold = random.randint(10, 20)
        player.gold += gold
        log.append(f"You find {gold} gold in an abandoned pouch.")
    else:
        log.append("The area is peaceful. Nothing happens.")

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
