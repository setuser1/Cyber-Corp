# === litrpg_game.py ===
# Full-featured game logic for LAN multiplayer (network-ready)

import random
import time

QUESTS = [
    {"id": 1, "name": "First Blood", "desc": "Defeat 1 enemy", "type": "kill", "goal": 1, "progress": 0, "completed": False, "reward": "Health Potion"},
    {"id": 2, "name": "Hunter", "desc": "Defeat 5 enemies", "type": "kill", "goal": 5, "progress": 0, "completed": False, "reward": "Steel Sword"},
    {"id": 3, "name": "Survivor", "desc": "Reach level 3", "type": "level", "goal": 3, "progress": 0, "completed": False, "reward": "Magic Scroll"},
]

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

    def get_status(self):
        return {
            "name": self.name,
            "role": self.role,
            "level": self.level,
            "hp": f"{self.hp}/{self.max_hp}",
            "xp": self.xp,
            "gold": self.gold,
            "mana": f"{getattr(self, 'mana', '-')}/{getattr(self, 'max_mana', '-')}" if self.role == "Mage" else None,
            "attack": self.attack,
            "inventory": self.inventory,
            "stat_points": self.stat_points,
            "quests": self.quests
        }

class Enemy:
    def __init__(self, name, hp, attack, xp_reward):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.xp_reward = xp_reward

    def to_dict(self):
        return {
            "name": self.name,
            "hp": self.hp,
            "attack": self.attack
        }

def assign_quests(player):
    for quest in QUESTS:
        qcopy = dict(quest)
        if not any(q["id"] == qcopy["id"] for q in player.quests):
            player.quests.append(qcopy)

def check_quests(player, type_, value=1):
    completed = []
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
            completed.append(quest["name"])
    return completed

def check_level_up(player):
    logs = []
    while player.xp >= player.level * 100:
        player.level += 1
        player.stat_points += 3
        player.max_hp += 10
        player.hp = player.max_hp
        player.attack += 2
        logs.append(f"{player.name} leveled up to {player.level}!")
        if player.role == "Mage":
            player.max_mana += 10
            player.mana = player.max_mana
            player.spell_power += 2
        completed = check_quests(player, "level")
        for quest in completed:
            logs.append(f"Quest Complete: {quest}!")
    return logs

def simulate_battle(player, enemy):
    battle_log = []
    bleed_turns = 0

    while player.hp > 0 and enemy.hp > 0:
        damage = player.attack
        if player.role == "Mage" and getattr(player, 'mana', 0) >= 10:
            damage += player.spell_power
            player.mana -= 10
            battle_log.append(f"{player.name} casts Fireball for {damage} damage!")
        else:
            battle_log.append(f"{player.name} attacks {enemy.name} for {damage} damage!")

        enemy.hp -= damage

        if enemy.hp <= 0:
            break

        enemy_damage = enemy.attack
        player.hp -= enemy_damage
        battle_log.append(f"{enemy.name} hits {player.name} for {enemy_damage} damage!")

    if player.hp > 0:
        battle_log.append(f"{player.name} defeated {enemy.name} and earned {enemy.xp_reward} XP!")
        player.xp += enemy.xp_reward
        level_log = check_level_up(player)
        battle_log.extend(level_log)
        quest_log = check_quests(player, "kill")
        for quest in quest_log:
            battle_log.append(f"Quest Complete: {quest}!")
    else:
        battle_log.append(f"{player.name} was defeated by {enemy.name}...")

    return battle_log

def explore(player):
    outcome = random.random()
    log = []
    if outcome < 0.6:
        enemy_pool = [
            ("Goblin", 30, 5, 20),
            ("Skeleton", 40, 7, 25),
            ("Wolf", 35, 6, 22),
            ("Orc", 50, 10, 30),
        ]
        e = random.choice(enemy_pool)
        enemy = Enemy(*e)
        log.append(f"You encountered a {enemy.name}!")
        battle_log = simulate_battle(player, enemy)
        log.extend(battle_log)
    elif outcome < 0.8:
        heal = random.randint(10, 25)
        player.hp = min(player.max_hp, player.hp + heal)
        log.append(f"You found a healing spring and regained {heal} HP!")
    else:
        gold = random.randint(5, 15)
        player.gold += gold
        log.append(f"You found {gold} gold on the ground!")
    return log

def use_item(player, item, players):
    log = []
    used = False
    if item == "Health Potion":
        if player.hp < player.max_hp:
            heal = min(30, player.max_hp - player.hp)
            player.hp += heal
            log.append(f"{player.name} used a Health Potion and restored {heal} HP!")
            used = True
    elif item == "Mana Potion" and player.role == "Mage":
        if player.mana < player.max_mana:
            regen = min(30, player.max_mana - player.mana)
            player.mana += regen
            log.append(f"{player.name} used a Mana Potion and restored {regen} MP!")
            used = True
    elif item == "Magic Scroll" and player.role == "Mage":
        player.spell_power += 1
        log.append(f"{player.name} used a Magic Scroll. Spell Power +1!")
        used = True
    elif item == "Steel Sword":
        player.attack += 2
        log.append(f"{player.name} equipped the Steel Sword. Attack +2!")
        used = True
    elif item == "Bleed Enchantment":
        player.bleed_chance += 10
        log.append(f"{player.name} gained Bleed Enchantment. Bleed Chance +10%!")
        used = True
    elif item == "Phoenix Feather":
        unconscious = [p for p in players if p != player and p.hp <= 0]
        if unconscious:
            revived = unconscious[0]
            revived.hp = revived.max_hp // 2
            log.append(f"{player.name} revived {revived.name} with a Phoenix Feather!")
            used = True
        else:
            log.append("No unconscious teammates to revive.")
    else:
        log.append(f"{item} can't be used right now.")

    if used:
        player.inventory.remove(item)
    return log
