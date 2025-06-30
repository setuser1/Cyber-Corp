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
