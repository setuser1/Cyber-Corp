import random

class Player:
    def __init__(self, name, role="Warrior"):
        self.name = name
        self.role = role
        self.level = 1
        self.xp = 0
        self.gold = 100
        self.hp = 90 if role == "Mage" else 100
        self.max_hp = self.hp
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
    def __init__(self, name, hp, atk, xp, has_bleed_enchantment=False):
        self.name = name
        self.hp = hp
        self.attack = atk
        self.xp_reward = xp
        self.has_bleed_enchantment = has_bleed_enchantment

# ========== Quest System ==========
QUESTS = [
    {"id": 1, "name": "First Blood", "desc": "Defeat 1 enemy", "type": "kill", "goal": 1, "progress": 0, "completed": False, "reward": "Health Potion"},
    {"id": 2, "name": "Hunter", "desc": "Defeat 5 enemies", "type": "kill", "goal": 5, "progress": 0, "completed": False, "reward": "Steel Sword"},
    {"id": 3, "name": "Survivor", "desc": "Reach level 3", "type": "level", "goal": 3, "progress": 0, "completed": False, "reward": "Magic Scroll"},
]

def assign_quests(player):
    for quest in QUESTS:
        q = dict(quest)
        if q not in player.quests:
            player.quests.append(q)

def check_quests(player, type_, value=1):
    log = []
    for q in player.quests:
        if q["completed"]:
            continue
        if q["type"] == type_:
            if type_ == "kill":
                q["progress"] += value
            elif type_ == "level" and player.level >= q["goal"]:
                q["progress"] = q["goal"]
        if q["progress"] >= q["goal"]:
            q["completed"] = True
            player.inventory.append(q["reward"])
            log.append(f"✓ Quest Complete: {q['name']}! You received a {q['reward']}!")
    return log

# ========== Game Actions ==========

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

def explore(player, all_players=None):
    log = [f"{player.name} explores the wilds..."]
    outcome = random.random()

    if outcome < 0.6:
        enemy_data = random.choice([
            ("Goblin", 30, 5, 20), ("Skeleton", 40, 7, 25),
            ("Wolf", 35, 6, 22), ("Bat", 25, 4, 15),
            ("Orc", 50, 10, 30), ("Troll", 60, 12, 40),
            ("Giant", 70, 15, 50)
        ])
        enemy = Enemy(*enemy_data, has_bleed_enchantment=(random.random() < 0.05))

        # Mage decides to cast a spell if mana allows
        if player.role == "Mage" and player.mana >= 10:
            damage = player.attack + player.spell_power
            player.mana -= 10
            log.append(f"{player.name} casts Fireball at {enemy.name} for {damage} damage!")
        else:
            damage = player.attack
            log.append(f"{player.name} attacks the {enemy.name} for {damage} damage!")

        enemy.hp -= damage

        if enemy.hp <= 0:
            player.xp += enemy.xp_reward
            log.append(f"{player.name} defeated the {enemy.name} and gained {enemy.xp_reward} XP.")
            if player.xp >= player.level * 100:
                level_up(player)
                log.append(f"{player.name} leveled up to {player.level}!")
            log += check_quests(player, "kill")
        else:
            dmg = enemy.attack
            player.hp = max(0, player.hp - dmg)
            log.append(f"The {enemy.name} hits back for {dmg} damage!")

    elif outcome < 0.7:
        heal = random.randint(10, 30)
        player.hp = min(player.max_hp, player.hp + heal)
        log.append(f"{player.name} found a health spring and restored {heal} HP.")
    elif outcome < 0.8:
        gold = random.randint(10, 20)
        player.gold += gold
        log.append(f"{player.name} found {gold} gold!")
    else:
        log.append("Nothing happened.")

    return log

def use_item(player, item, players):
    log = []
    if item not in player.inventory:
        return [f"{item} not in inventory."]

    used = False
    if item == "Health Potion":
        if player.hp < player.max_hp:
            heal = min(30, player.max_hp - player.hp)
            player.hp += heal
            log.append(f"{player.name} used a Health Potion and healed {heal} HP.")
            used = True
        else:
            log.append("Already at full HP.")
    elif item == "Mana Potion" and player.role == "Mage":
        if player.mana < player.max_mana:
            regen = min(30, player.max_mana - player.mana)
            player.mana += regen
            log.append(f"{player.name} used a Mana Potion and regained {regen} MP.")
            used = True
        else:
            log.append("Already at full mana.")
    elif item == "Magic Scroll" and player.role == "Mage":
        player.spell_power += 1
        log.append(f"{player.name} read the Magic Scroll. Spell power increased!")
        used = True
    elif item == "Steel Sword":
        player.attack += 2
        log.append(f"{player.name} equipped a Steel Sword. Attack +2!")
        used = True
    elif item == "Bleed Enchantment":
        player.bleed_chance += 10
        log.append(f"{player.name}'s weapon is now bleeding. +10% bleed chance.")
        used = True
    elif item == "Phoenix Feather":
        unconscious = [p for p in players if p != player and p.hp <= 0]
        if unconscious:
            target = unconscious[0]
            target.hp = target.max_hp // 2
            log.append(f"{player.name} used a Phoenix Feather to revive {target.name}!")
            used = True
        else:
            log.append("No teammates to revive.")
    else:
        log.append(f"{item} had no effect.")

    if used:
        player.inventory.remove(item)
    return log

def allocate_stats(player):
    log = []
    if player.stat_points <= 0:
        return ["No stat points to allocate."]

    # For demo purposes, just increase attack
    while player.stat_points > 0:
        player.attack += 1
        player.stat_points -= 1
        log.append(f"{player.name} increased attack to {player.attack}.")
    return log

def show_quests(player):
    lines = ["--- Quest Log ---"]
    for q in player.quests:
        status = "✓" if q["completed"] else f"{q['progress']}/{q['goal']}"
        lines.append(f"{q['name']} - {q['desc']} ({status})")
    return lines

def visit_shop(player):
    log = []
    shop_items = {
        "Health Potion": 20,
        "Mana Potion": 25,
        "Magic Scroll": 40,
        "Steel Sword": 50,
        "Bleed Enchantment": 60,
        "Phoenix Feather": 150
    }

    # For now just show and auto-buy Health Potion if enough gold
    item = "Health Potion"
    if player.gold >= shop_items[item]:
        player.gold -= shop_items[item]
        player.inventory.append(item)
        log.append(f"{player.name} bought a {item}.")
    else:
        log.append(f"{player.name} can't afford a {item}.")

    return log

def revive_teammate(player, players):
    log = []
    unconscious = [p for p in players if p != player and p.hp <= 0]
    if not unconscious:
        return ["No teammates need revival."]

    if "Phoenix Feather" in player.inventory:
        target = unconscious[0]
        target.hp = target.max_hp // 2
        player.inventory.remove("Phoenix Feather")
        log.append(f"{player.name} revived {target.name} with a Phoenix Feather!")
    else:
        log.append("You need a Phoenix Feather to revive a teammate.")
    return log

def player_turn_done():
    return ["Turn complete."]
