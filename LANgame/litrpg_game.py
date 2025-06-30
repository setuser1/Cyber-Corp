import random

ITEMS = {
    "Health Potion": {"effect": "heal", "value": 30, "cost": 10},
    "Mana Potion": {"effect": "mana", "value": 20, "cost": 12},
    "Phoenix Feather": {"effect": "revive", "value": 50, "cost": 40},
    "Throwing Knife": {"effect": "damage", "value": 10, "cost": 8}
}

class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.xp = 0
        self.level = 1
        self.xp_needed = 20
        self.inventory = []
        self.gold = 50
        self.stat_points = 0
        self.quests = []
        self.bleed = 0
        self.alive = True
        if role == "Mage":
            self.mana = 30
            self.max_mana = 30
            self.spell_power = 15

    def to_dict(self):
        return self.__dict__

    def from_dict(self, data):
        self.__dict__.update(data)

def assign_quests(player):
    if not player.quests:
        player.quests = ["Defeat 3 enemies", "Reach level 3", "Collect 100 gold"]

def check_quests(player, log):
    if "Defeat 3 enemies" in player.quests and player.xp >= 30:
        log.append(f"{player.name} completed quest: Defeat 3 enemies!")
        player.quests.remove("Defeat 3 enemies")
        player.gold += 20
    if "Reach level 3" in player.quests and player.level >= 3:
        log.append(f"{player.name} completed quest: Reach level 3!")
        player.quests.remove("Reach level 3")
        player.gold += 30
    if "Collect 100 gold" in player.quests and player.gold >= 100:
        log.append(f"{player.name} completed quest: Collect 100 gold!")
        player.quests.remove("Collect 100 gold")
        player.gold += 50

def level_up(player, log):
    while player.xp >= player.xp_needed:
        player.level += 1
        player.xp -= player.xp_needed
        player.xp_needed += 10
        player.stat_points += 2
        log.append(f"{player.name} leveled up to {player.level}! +2 stat points!")

def allocate_stats(player):
    log = []
    while player.stat_points > 0:
        log.append(f"{player.name} has {player.stat_points} stat points.")
        options = ["1. +10 Max HP", "2. +2 Attack"]
        if player.role == "Mage":
            options += ["3. +10 Max Mana", "4. +5 Spell Power"]
        log.extend(options)
        # Default to increasing HP for placeholder logic
        choice = "1"
        if choice == "1":
            player.max_hp += 10
            player.hp += 10
        elif choice == "2":
            player.attack += 2
        elif choice == "3" and player.role == "Mage":
            player.max_mana += 10
            player.mana += 10
        elif choice == "4" and player.role == "Mage":
            player.spell_power += 5
        player.stat_points -= 1
    return log

def explore(player, players):
    log = []
    enemy_hp = 40
    enemy_attack = 8
    enemy_bleed = 0
    log.append(f"{player.name} encountered a wild enemy!")

    while enemy_hp > 0 and player.hp > 0:
        if player.role == "Mage" and player.mana >= 10:
            log.append(f"{player.name} casts Fireball!")
            damage = player.spell_power + random.randint(5, 10)
            player.mana -= 10
        else:
            damage = player.attack + random.randint(0, 5)
            log.append(f"{player.name} attacks for {damage} damage.")

        enemy_hp -= damage
        if enemy_hp <= 0:
            log.append("Enemy defeated!")
            gained = 10
            player.xp += gained
            player.gold += 10
            check_quests(player, log)
            level_up(player, log)
            return log

        # Enemy attacks
        enemy_damage = enemy_attack + random.randint(0, 3)
        player.hp -= enemy_damage
        log.append(f"Enemy hits {player.name} for {enemy_damage} damage.")

        if player.bleed > 0:
            player.hp -= player.bleed
            log.append(f"{player.name} takes {player.bleed} bleed damage.")
            player.bleed = max(0, player.bleed - 1)

        if player.hp <= 0:
            log.append(f"{player.name} was defeated...")
            player.alive = False
            return log
    return log

def use_item(player, item_name, players):
    log = []
    item = ITEMS.get(item_name)
    if item and item_name in player.inventory:
        if item["effect"] == "heal":
            player.hp = min(player.max_hp, player.hp + item["value"])
            log.append(f"{player.name} heals for {item['value']} HP.")
        elif item["effect"] == "mana" and player.role == "Mage":
            player.mana = min(player.max_mana, player.mana + item["value"])
            log.append(f"{player.name} restores {item['value']} mana.")
        elif item["effect"] == "damage":
            log.append(f"{player.name} throws a knife! Bonus {item['value']} damage next turn.")
            player.attack += item["value"]
        elif item["effect"] == "revive":
            for target in players:
                if not target.alive and target != player:
                    target.hp = item["value"]
                    target.alive = True
                    log.append(f"{player.name} revived {target.name} with a Phoenix Feather!")
                    break
        player.inventory.remove(item_name)
    else:
        log.append(f"{item_name} is not available.")
    return log

def show_quests(player):
    return [f"Quest: {q}" for q in player.quests] if player.quests else ["No active quests."]

def visit_shop(player):
    log = ["Welcome to the shop!"]
    shop_items = random.sample(list(ITEMS.keys()), 3)
    for idx, name in enumerate(shop_items):
        item = ITEMS[name]
        log.append(f"{idx+1}. {name} - {item['cost']} gold")
    selection = 0  # Placeholder: buy first item
    selected = shop_items[selection]
    item = ITEMS[selected]
    if player.gold >= item["cost"]:
        player.gold -= item["cost"]
        player.inventory.append(selected)
        log.append(f"Bought {selected}.")
    else:
        log.append("Not enough gold.")
    return log

def revive_teammate(player, players):
    log = []
    for teammate in players:
        if not teammate.alive and teammate != player:
            teammate.hp = 30
            teammate.alive = True
            log.append(f"{player.name} revived {teammate.name}!")
            break
    if not log:
        log.append("No teammate to revive.")
    return log

def player_turn_done():
    return ["Turn complete."]
