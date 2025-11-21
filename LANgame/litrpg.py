import os
import random
import json
import time
import datetime

# -------------------------------
# Spells Database and Menu Function
# -------------------------------
SPELLS = {
    "Mage": [
        {
            "name": "Fireball",
            "cost_type": "mana",
            "cost": 10,
            "description": "Deal spell power + attack damage.",
            "effect": "fireball"
        }
        ,
        {
            "name": "Meteor Shower",
            "cost_type": "mana",
            "cost": 18,
            "description": "A meteor shower that strikes multiple enemies (AoE).",
            "effect": "firestorm"
        }
    ],
    "Warlock": [
        {
            "name": "Eldritch Blast",
            "cost_type": "mana",
            "cost": 10,
            "description": "Deal spell power + attack + d5 damage.",
            "effect": "eldritch_blast"
        },
        {
            "name": "Hellfire",
            "cost_type": "hp",
            "cost": 10,
            "description": "Sacrifice HP for massive attack.",
            "effect": "hellfire"
        }
        ,
        {
            "name": "Shadow Nova",
            "cost_type": "mana",
            "cost": 15,
            "description": "Unleash a nova of shadow that damages all nearby enemies (AoE).",
            "effect": "shadow_nova"
        }
    ]
}

# Developer-only access password (can be overridden by env var LITRPG_DEV_PASSWORD)
DEV_PASSWORD = os.environ.get("LITRPG_DEV_PASSWORD", "devpass")

# -------------------------------
# Cultivator Realms (data-driven)
# Add or reorder entries here to create new realms easily.
# Each realm fires once when the cultivator reaches the required level.
CULTIVATOR_REALMS = [
    {"name": "Qi Novice", "level_req": 1, "qi_bonus": 0, "attack_multiplier": 1.0, "spell_power_bonus": 0, "description": "The beginning of cultivation."},
    {"name": "Foundation Establishment", "level_req": 3, "qi_bonus": 10, "attack_multiplier": 1.05, "spell_power_bonus": 2, "description": "A deeper connection to Qi."},
    {"name": "Core Formation", "level_req": 6, "qi_bonus": 20, "attack_multiplier": 1.12, "spell_power_bonus": 4, "description": "Your core consolidates, strength grows."},
    {"name": "Nascent Soul", "level_req": 9, "qi_bonus": 35, "attack_multiplier": 1.20, "spell_power_bonus": 8, "description": "A nascent soul forms within."},
    {"name": "Spirit Ascendant", "level_req": 12, "qi_bonus": 60, "attack_multiplier": 1.35, "spell_power_bonus": 15, "description": "You touch the spirit realm itself."},
]


def attempt_realm_breakthrough(player, consume_pill=True):
    """
    Attempt to advance the player's cultivator realm if they meet the level requirement.
    If `consume_pill` is True, the function will require a 'Breakthrough Pill' in the player's inventory
    and consume it on success. Returns True if a breakthrough was applied, False otherwise.
    """
    if player.role != "Cultivator":
        print("Only Cultivators can attempt realm breakthroughs.")
        return False

    # Find the next realm index
    next_index = player.realm_stage + 1
    if next_index >= len(CULTIVATOR_REALMS):
        print("You have already reached the highest known realm.")
        return False

    next_realm = CULTIVATOR_REALMS[next_index]
    req = next_realm.get("level_req", 9999)
    if player.level < req:
        print(f"You are not yet ready for {next_realm.get('name')}. Reach level {req} to attempt breakthrough.")
        return False

    # Check for pill if consumption required
    pill_name = "Breakthrough Pill"
    has_pill = pill_name in player.inventory
    if consume_pill and not has_pill:
        print(f"A {pill_name} is required to break through to {next_realm.get('name')}.")
        return False

    # Apply realm bonuses
    player.realm_stage = next_index
    player.realm_name = next_realm.get("name")
    qi_bonus = next_realm.get("qi_bonus", 0)
    player.max_qi = getattr(player, 'max_qi', 0) + qi_bonus
    player.qi = player.max_qi
    mult = next_realm.get("attack_multiplier", 1.0)
    player.attack = max(1, int(player.attack * mult))
    player.spell_power += next_realm.get("spell_power_bonus", 0)

    print(f"\n*** {player.name} broke through the realm: {player.realm_name}! Stat points +3 ***")

    if consume_pill and has_pill:
        # consume one pill from inventory
        try:
            player.inventory.remove(pill_name)
            print(f"{pill_name} consumed.")
        except ValueError:
            pass

    return True


# Add Cultivator starting spells (developer-only)
SPELLS.setdefault("Cultivator", [
    {
        "name": "Qi Strike",
        "cost_type": "qi",
        "cost": 10,
        "description": "Strike using cultivated Qi to deal spell_power + attack damage.",
        "effect": "qi_strike"
    }
])

def cast_spell_menu(player):
    available_spells = SPELLS.get(player.role, [])
    if not available_spells:
        print("You have no spells to cast.")
        return None

    print("\nWhich spell would you like to cast?")
    for idx, sp in enumerate(available_spells, 1):
        if sp["cost_type"] == "mana":
            affordable = getattr(player, 'mana', 0) >= sp["cost"]
        elif sp["cost_type"] == "qi":
            affordable = getattr(player, 'qi', 0) >= sp["cost"]
        elif sp["cost_type"] == "hp":
            affordable = player.hp > sp["cost"]
        else:
            affordable = True
        aff_text = "(Enough)" if affordable else "(Can't Afford)"
        print(f"{idx}. {sp['name']} - Costs {sp['cost']} {sp['cost_type']} {aff_text}\n   {sp['description']}")
    print("0. Cancel")

    choice = input("Choose your spell (number): ").strip()
    if choice == "0":
        return None
    try:
        spell_idx = int(choice) - 1
        if not (0 <= spell_idx < len(available_spells)):
            print("Invalid spell choice.")
            return None
        selected_spell = available_spells[spell_idx]
        # Affordability check
        if selected_spell["cost_type"] == "mana" and getattr(player, 'mana', 0) < selected_spell["cost"]:
            print("Not enough mana!")
            return None
        if selected_spell["cost_type"] == "qi" and getattr(player, 'qi', 0) < selected_spell["cost"]:
            print("Not enough Qi!")
            return None
        if selected_spell["cost_type"] == "hp" and player.hp <= selected_spell["cost"]:
            print("Not enough HP!")
            return None
        return selected_spell
    except:
        print("Invalid input.")
        return None

# -------------------------------
# Skills Database and Menu
# -------------------------------
SKILLS = {
    "Warrior": [
        {
            "name": "Cleave",
            "cooldown": 3,
            "description": "A heavy strike that deals extra damage.",
            "effect": "cleave",
            "power": 5
        },
        {
            "name": "Whirlwind",
            "cooldown": 5,
            "description": "Spin and hit all nearby enemies for moderate damage (AoE).",
            "effect": "whirlwind",
            "power": 8
        },
        {
            "name": "Berserk",
            "cooldown": 5,
            "description": "A furious attack that deals big damage but costs a bit of HP.",
            "effect": "berserk",
            "power": 10,
            "self_hp_cost": 8
        }
    ],
    # Placeholder: mages/warlocks could have active skills later
    "Mage": [],
    "Warlock": []
}

# Cultivator skills (developer-only)
SKILLS.setdefault("Cultivator", [
    {
        "name": "Flowing Palm",
        "cooldown": 3,
        "description": "A precise strike that scales with Qi.", 
        "effect": "flowing_palm",
        "power": 20
    },
    {
        "name": "Overcharge",
        "cooldown": 6,
        "description": "Channel Qi to greatly increase next attack at cost of Qi.",
        "effect": "overcharge",
        "power": 30,
        "qi_cost": 15
    }
    ,
    {
        "name": "Qi Wave",
        "cooldown": 5,
        "description": "Release a wave of Qi that damages all enemies (AoE).",
        "effect": "qi_wave",
        "power": 12,
        "qi_cost": 12
    }
])


def use_skill_menu(player):
    available_skills = SKILLS.get(player.role, [])
    if not available_skills:
        print("You have no class skills.")
        return None

    print("\nWhich skill would you like to use?")
    for idx, sk in enumerate(available_skills, 1):
        cd = player.skill_cooldowns.get(sk["name"], 0)
        ready = "(Ready)" if cd <= 0 else f"(CD: {cd})"
        print(f"{idx}. {sk['name']} - {sk['description']} {ready}")
    print("0. Cancel")

    choice = input("Choose your skill (number): ").strip()
    if choice == "0":
        return None
    try:
        sk_idx = int(choice) - 1
        if not (0 <= sk_idx < len(available_skills)):
            print("Invalid skill choice.")
            return None
        selected_skill = available_skills[sk_idx]
        # Check cooldown
        if player.skill_cooldowns.get(selected_skill['name'], 0) > 0:
            print("That skill is on cooldown.")
            return None
        return selected_skill
    except:
        print("Invalid input.")
        return None

# -------------------------------
# Player and Enemy Classes
# -------------------------------
# Centralize class definitions
CLASS_DEFS = {
    "Warrior": {
        "hp": 100, "max_hp": 100,
        "mana": 0, "max_mana": 0,
        "attack": 10,
        "spell_power": 0,
        "spell_list": [],
        "skill_list": [
            {"name": "Cleave", "cooldown": 3, "effect": "cleave", "power": 5},
            {"name": "Berserk", "cooldown": 5, "effect": "berserk", "power": 10, "self_hp_cost": 8}
        ],
        "stat_options": ["1. Max HP (+4)", "2. Attack (+1)"]
    },
    "Mage": {
        "hp": 75, "max_hp": 75,
        "mana": 50, "max_mana": 50,
        "attack": 10,
        "spell_power": 10,
        "spell_list": [
            {"name": "Fireball", "cost_type": "mana", "cost": 10, "effect": "fireball", "description": "Deal spell power + attack damage."}
        ],
        "skill_list": [],
        "stat_options": ["1. Max HP (+4)", "2. Attack (+1)", "3. Max Mana (+5)", "4. Spell Power (+1)"]
    },
    "Warlock": {
        "hp": 80, "max_hp": 80,
        "mana": 30, "max_mana": 30,
        "attack": 10,
        "spell_power": 10,
        "spell_list": [
            {"name": "Eldritch Blast", "cost_type": "mana", "cost": 10, "effect": "eldritch_blast", "description": "Deal spell power + attack + d5 damage."},
            {"name": "Hellfire", "cost_type": "hp", "cost": 10, "effect": "hellfire", "description": "Sacrifice HP for massive attack."}
        ],
        "skill_list": [],
        "stat_options": ["1. Max HP (+4)", "2. Attack (+1)", "3. Max Mana (+5)", "4. Spell Power (+1)"]
    },
    "Cultivator": {
        "hp": 100, "max_hp": 100,
        "qi": 100, "max_qi": 100,
        "attack": 20,
        "spell_power": 30,
        "spell_list": [
            {"name": "Qi Strike", "cost_type": "qi", "cost": 10, "effect": "qi_strike", "description": "Strike using cultivated Qi to deal spell_power + attack damage."}
        ],
        "skill_list": [
            {"name": "Flowing Palm", "cooldown": 3, "effect": "flowing_palm", "power": 20},
            {"name": "Overcharge", "cooldown": 6, "effect": "overcharge", "power": 30, "qi_cost": 15}
        ],
        "stat_options": ["1. Max HP (+4)", "2. Attack (+1)", "3. Max Qi (+5)", "4. Spell Power (+1)"]
    },
}

def choose_player_class():
    print("Choose your class:")
    for idx, class_name in enumerate(CLASS_DEFS.keys(), 1):
        print(f"{idx}. {class_name}")
    choice = input("Enter the number for your class (leave blank for default): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(CLASS_DEFS):
        role = list(CLASS_DEFS.keys())[int(choice) - 1]
    else:
        role = list(CLASS_DEFS.keys())[0]  # Default to first class (Warrior, etc)

    # Developer-only class protection
    if role == "Cultivator":
        pwd = input("Developer class selected. Enter developer password to unlock (leave blank to cancel): ").strip()
        if not pwd or pwd != DEV_PASSWORD:
            print("Access denied or cancelled. Defaulting to Warrior.")
            role = list(CLASS_DEFS.keys())[0]

    return role

class Player:
    def __init__(self, name, role="Warrior"):
        self.name = name
        self.role = role
        self.level = 1
        self.xp = 0
        self.gold = 100
        self.stat_points = 0
        self.inventory = []
        self.bleed_chance = 0
        self.quests = []
        # Load properties from CLASS_DEFS
        cfg = CLASS_DEFS.get(role, CLASS_DEFS["Warrior"])
        self.hp = cfg["hp"]
        self.max_hp = cfg["max_hp"]
        # Support both classic 'mana' and Cultivator's 'qi'. Only initialize Qi for Cultivator.
        self.mana = cfg.get("mana", 0)
        self.max_mana = cfg.get("max_mana", 0)
        if role == "Cultivator":
            self.qi = cfg.get("qi", 0)
            self.max_qi = cfg.get("max_qi", 0)
        else:
            self.qi = 0
            self.max_qi = 0
        # Keep base stats for exponential scaling (especially for Cultivator)
        self.base_attack = cfg.get("attack", 1)
        self.base_spell_power = cfg.get("spell_power", 0)
        self.attack = int(self.base_attack)
        self.spell_power = int(self.base_spell_power)
        # Cultivation tracking
        if role == "Cultivator":
            # start at realm index 0 (Qi Novice)
            self.realm_stage = 0
            self.realm_name = CULTIVATOR_REALMS[0]["name"] if CULTIVATOR_REALMS else ""
        else:
            self.realm_stage = -1
            self.realm_name = None
        self.spell_list = cfg.get("spell_list", [])
        self.stat_options = cfg.get("stat_options", [])
        # Skills and cooldown tracking
        self.skill_list = cfg.get("skill_list", [])
        self.skill_cooldowns = {}

    def show_status(self):
        print(f"\nName: {self.name} ({self.role})\nLevel: {self.level}  XP: {self.xp}\nHP: {self.hp}/{self.max_hp}  Gold: {self.gold}")
        # Show resource depending on class (Mana or Qi)
        if getattr(self, 'max_qi', 0) > 0:
            print(f"Qi: {getattr(self, 'qi', 0)}/{getattr(self, 'max_qi', 0)}  Spell Power: {self.spell_power}")
        elif self.max_mana > 0:
            print(f"Mana: {self.mana}/{self.max_mana}  Spell Power: {self.spell_power}")
        print(f"Attack: {self.attack}")
        # Show current cultivator realm if applicable
        if self.role == "Cultivator":
            print(f"Realm: {getattr(self, 'realm_name', 'Unknown')} (Stage {getattr(self, 'realm_stage', -1)})")
        # Show skill cooldowns
        if self.skill_list:
            cds = ", ".join([f"{s['name']}: {self.skill_cooldowns.get(s['name'],0)}" for s in self.skill_list])
            print(f"Skills cooldowns: {cds}")

def allocate_stats(player):
    if player.stat_points <= 0:
        print("\nNo stat points to allocate.")
        return
    print(f"\nYou have {player.stat_points} stat points.")
    print("\n" + "\n".join(player.stat_options))

class Enemy:
    def __init__(self, name, hp, attack, xp_reward, has_bleed_enchantment=False):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.xp_reward = xp_reward
        self.has_bleed_enchantment = has_bleed_enchantment


def maybe_drop_breakthrough_pill(enemy, player):
    """Chance to drop a Breakthrough Pill depending on enemy strength."""
    # Very simple mapping by boss name
    drops = {
        "Spirit Lord": 0.20,
        "Elder Dragon": 0.10,
        "Abyssal Warden": 0.06,
        "Giant": 0.01,
        "Troll": 0.005,
        "Orc": 0.002,
    }
    chance = drops.get(enemy.name, 0.0005)  # tiny chance for common enemies
    roll = random.random()
    if roll < chance:
        player.inventory.append("Breakthrough Pill")
        print(f"\nThe {enemy.name} dropped a Breakthrough Pill! It has been added to your inventory.")
        # If the player already meets any quest's level requirement that requires this item, auto-consume to complete
        for quest in player.quests:
            if quest.get('completed'):
                continue
            if quest.get('requires_item') == 'Breakthrough Pill' and quest['type'] == 'level' and player.level >= quest.get('goal', 0):
                # consume and apply breakthrough
                attempt_realm_breakthrough(player, consume_pill=True)
                quest['completed'] = True
                reward = quest.get('reward')
                if reward:
                    player.inventory.append(reward)
                    print(f"\nQuest Complete: {quest['name']}! You received a {reward}!")
                break
        return True
    return False

# -------------------------------
# Quest System
# -------------------------------
QUESTS = [
    {"id": 1, "name": "First Blood", "desc": "Defeat 1 enemy", "type": "kill", "goal": 1, "progress": 0, "completed": False, "reward": "Health Potion"},
    {"id": 2, "name": "Hunter", "desc": "Defeat 5 enemies", "type": "kill", "goal": 5, "progress": 0, "completed": False, "reward": "Steel Sword"},
    {"id": 3, "name": "Survivor", "desc": "Reach level 3", "type": "level", "goal": 3, "progress": 0, "completed": False, "reward": "Magic Scroll"},
    # Breakthrough Trial now requires the player to reach level AND use a Breakthrough Pill to complete
    {"id": 4, "name": "Breakthrough Trial", "desc": "Reach level 6 and use a Breakthrough Pill to prove your readiness.", "type": "level", "goal": 6, "progress": 0, "completed": False, "reward": "Magic Scroll", "role": "Cultivator", "requires_item": "Breakthrough Pill"},
    # Mid-level cultivator quest that rewards a Breakthrough Pill (assigned only when player is experienced)
    {"id": 5, "name": "Warden's Trial", "desc": "Defeat a powerful foe to earn a Breakthrough Pill.", "type": "kill", "goal": 1, "progress": 0, "completed": False, "reward": "Breakthrough Pill", "role": "Cultivator", "min_level": 6},
]

def assign_quests(player):
    for quest in QUESTS:
        quest_copy = dict(quest)  # Make a copy
        if "progress" not in quest_copy:
            quest_copy["progress"] = 0
        # If quest has a role restriction, only assign to players with that role
        if quest_copy.get("role") and quest_copy.get("role") != player.role:
            continue
        # If quest has min_level, only assign when player meets it
        if quest_copy.get("min_level") and player.level < quest_copy.get("min_level"):
            continue
        if quest_copy not in player.quests:
            player.quests.append(quest_copy)

def check_quests(player, type_, value=1):
    for quest in player.quests:
        if quest["completed"]:
            continue
        if quest["type"] == type_:
            if type_ == "kill":
                quest["progress"] += value
            elif type_ == "level" and player.level >= quest["goal"]:
                # If the quest requires an item, don't auto-complete on level reach.
                if quest.get("requires_item"):
                    quest["progress"] = quest["goal"]
                    print(f"You meet the level requirement for '{quest['name']}'. Use or obtain a {quest.get('requires_item')} to complete it.")
                else:
                    quest["progress"] = quest["goal"]
        if quest["progress"] >= quest["goal"]:
            # Only auto-complete if no required item
            if not quest.get("requires_item"):
                quest["completed"] = True
                player.inventory.append(quest["reward"])
                print(f"\nQuest Complete: {quest['name']}! You received a {quest['reward']}!")

def show_quests(player):
    print("\n==== Quest Log ====")
    for quest in player.quests:
        status = "✓" if quest["completed"] else f"{quest.get('progress', 0)}/{quest['goal']}"
        print(f"{quest['name']} - {quest['desc']} ({status})")
    input("Press Enter to continue...")

# -------------------------------
# Exploration System
# -------------------------------
def explore(current_player, all_players):
    print(f"\n{current_player.name} ventures into the wilds...")
    time.sleep(1)
    outcome = random.random()

    if outcome < 0.6:
        # Normal enemy encounter, with a chance to be a multi-enemy ambush
        enemy_pool = [
            {"name": "Bat", "hp": 25, "attack": 4, "xp": 15, "min_level": 1},
            {"name": "Goblin", "hp": 30, "attack": 5, "xp": 20, "min_level": 1},
            {"name": "Skeleton", "hp": 40, "attack": 7, "xp": 25, "min_level": 1},
            {"name": "Wolf", "hp": 35, "attack": 6, "xp": 22, "min_level": 1},
            {"name": "Orc", "hp": 50, "attack": 10, "xp": 30, "min_level": 3},
            {"name": "Troll", "hp": 60, "attack": 12, "xp": 40, "min_level": 4},
            {"name": "Giant", "hp": 80, "attack": 16, "xp": 70, "min_level": 6},
            {"name": "Abyssal Warden", "hp": 150, "attack": 30, "xp": 180, "min_level": 8},
            {"name": "Elder Dragon", "hp": 220, "attack": 40, "xp": 300, "min_level": 10},
            {"name": "Spirit Lord", "hp": 320, "attack": 55, "xp": 500, "min_level": 14}
        ]

        # Allow enemies appropriate to the player's level; weaker enemies may appear earlier
        enemies_allowed = [e for e in enemy_pool if current_player.level >= e.get('min_level', 1) or e.get('hp', 0) < 50]

        # 20% of encounters with enemies become multi-enemy ambushes
        if random.random() < 0.20:
            count = random.choice([2, 2, 3])  # bias towards 2 enemies, sometimes 3
            chosen = random.choices(enemies_allowed, k=count)
            enemies = [Enemy(e['name'], e['hp'], e['attack'], e['xp'], random.random() < 0.03) for e in chosen]

            # Use all living players if 2+ alive, otherwise the single current player
            living_players = [p for p in all_players if p.hp > 0]
            if len(living_players) >= 2:
                multi_enemy_battle(living_players, enemies)
            else:
                multi_enemy_battle([current_player], enemies)

        else:
            e = random.choice(enemies_allowed)
            enemy = Enemy(e['name'], e['hp'], e['attack'], e['xp'], random.random() < 0.03)

            # Only trigger group battle if there are 2 or more *alive* players
            living_players = [p for p in all_players if p.hp > 0]
            if len(living_players) >= 2:
                group_battle(living_players, enemy)
            else:
                battle(current_player, enemy)

    elif outcome < 0.7:
        heal = random.randint(10, 30)
        current_player.hp = min(current_player.max_hp, current_player.hp + heal)
        print(f"You discover a hidden cache and regain {heal} HP!")
    elif outcome < 0.8:
        gold_found = random.randint(10, 20)
        current_player.gold += gold_found
        print(f"You discover an abandoned wagon with {gold_found} gold inside!")
    else:
        print("The area is peaceful. You relax and enjoy the scenery.")

    input("\nPress Enter to return to the menu...")

# -------------------------------
# Battle System
# -------------------------------
def battle(player, enemy):
    print(f"\nA wild {enemy.name} appears! Prepare for battle!")
    bleed_turns = 0

    while enemy.hp > 0 and player.hp > 0:
        print(f"\n{player.name}: {player.hp} HP")
        # Show resource (Mana or Qi) depending on class
        if getattr(player, 'max_qi', 0) > 0:
            print(f"Qi: {getattr(player, 'qi', 0)}/{getattr(player, 'max_qi', 0)}")
        elif player.role in ("Mage", "Warlock") or player.max_mana > 0:
            print(f"Mana: {player.mana}/{player.max_mana}")
        print(f"{enemy.name}: {enemy.hp} HP")

        choice = input("Choose action: (1) Attack  (2) Use Inventory  (3) Use Skill: ").strip()

        if choice == '1':
            # Dynamic spell menu for Mage and Warlock
            if player.role in SPELLS:
                spell_choice = input("Cast spell? (y) Yes or (n) Normal Attack: ").strip().lower()
                if spell_choice == 'y':
                    spell = cast_spell_menu(player)
                    if not spell:
                        # cancelled or can't afford, skip applying spell
                        pass
                    else:
                        if spell["effect"] == "fireball":
                            damage = player.spell_power + player.attack
                            # deduct resource based on spell's cost_type
                            if spell.get("cost_type") == "mana":
                                player.mana -= spell.get("cost", 0)
                            elif spell.get("cost_type") == "qi":
                                player.qi -= spell.get("cost", 0)
                            print(f"You cast Fireball for {damage} damage!")
                        elif spell["effect"] in ("firestorm", "shadow_nova"):
                            # AoE spells used in single-target battle still deal strong damage
                            damage = player.spell_power + player.attack + 8
                            if spell.get("cost_type") == "mana":
                                player.mana -= spell.get("cost", 0)
                            elif spell.get("cost_type") == "qi":
                                player.qi -= spell.get("cost", 0)
                            print(f"You unleash {spell['name']} for {damage} damage!")
                        elif spell["effect"] == "qi_strike":
                            damage = player.spell_power + player.attack
                            if spell.get("cost_type") == "mana":
                                player.mana -= spell.get("cost", 0)
                            elif spell.get("cost_type") == "qi":
                                player.qi -= spell.get("cost", 0)
                            print(f"You channel Qi and strike for {damage} damage!")
                        elif spell["effect"] == "eldritch_blast":
                            damage = player.spell_power + player.attack + random.randint(1,5)
                            if spell.get("cost_type") == "mana":
                                player.mana -= spell.get("cost", 0)
                            elif spell.get("cost_type") == "qi":
                                player.qi -= spell.get("cost", 0)
                            print(f"You cast Eldritch Blast for {damage} damage!")
                        elif spell["effect"] == "hellfire":
                            damage = player.spell_power + player.attack + 15
                            player.hp -= spell.get("cost", 0)
                            print(f"You use Hellfire for {damage} damage at the cost of HP!")
                        else:
                            damage = player.attack
                else:
                    damage = player.attack
                    print(f"You attack the {enemy.name} for {damage} damage!")
            else:
                damage = player.attack
                print(f"You attack the {enemy.name} for {damage} damage!")

            if random.randint(1, 100) <= player.bleed_chance:
                bleed_turns = 3
                print("Bleed applied! Enemy will take damage for 3 turns.")

            enemy.hp -= damage

        elif choice == '2':
            used = manage_inventory(player, [player], in_battle=True)
            if not used:
                continue
        elif choice == '3':
            skill = use_skill_menu(player)
            if not skill:
                continue
            # Apply skill effects
            # Handle AoE skills for single-target battles as powerful single-target hits
            if skill['effect'] == 'cleave':
                damage = player.attack + skill.get('power', 0)
                print(f"You use {skill['name']} for {damage} damage!")
            elif skill['effect'] == 'flowing_palm':
                damage = player.spell_power + player.attack + skill.get('power', 0)
                print(f"You use {skill['name']} for {damage} Qi damage!")
            elif skill['effect'] == 'whirlwind':
                damage = player.attack + skill.get('power', 0) + 4
                # whirlwinds are physical and don't cost Qi by default
                print(f"You spin in a Whirlwind and strike for {damage} damage!")
            elif skill['effect'] == 'qi_wave':
                cost = skill.get('qi_cost', 0)
                if getattr(player, 'qi', 0) < cost:
                    print("Not enough Qi to use that skill!")
                    continue
                player.qi -= cost
                damage = player.spell_power + player.attack + skill.get('power', 0)
                print(f"You release a Qi Wave for {damage} damage! (cost {cost} Qi)")
            elif skill['effect'] == 'overcharge':
                # Support either mana_cost or qi_cost
                cost = skill.get('mana_cost', skill.get('qi_cost', 0))
                if skill.get('qi_cost') is not None or player.role == 'Cultivator':
                    if getattr(player, 'qi', 0) < cost:
                        print("Not enough Qi to use that skill!")
                        continue
                    player.qi -= cost
                    cost_label = 'Qi'
                else:
                    if getattr(player, 'mana', 0) < cost:
                        print("Not enough mana to use that skill!")
                        continue
                    player.mana -= cost
                    cost_label = 'mana'
                damage = player.attack + skill.get('power', 0) + player.spell_power
                print(f"You overcharge and deal {damage} damage (cost {cost} {cost_label})!")
            elif skill['effect'] == 'berserk':
                damage = player.attack + skill.get('power', 0)
                self_cost = skill.get('self_hp_cost', 0)
                player.hp = max(1, player.hp - self_cost)
                print(f"You go berserk! {skill['name']} deals {damage} damage but costs {self_cost} HP.")
            else:
                damage = player.attack
                print(f"You use {skill['name']} for {damage} damage!")

            # put skill on cooldown
            player.skill_cooldowns[skill['name']] = skill.get('cooldown', 1)
            enemy.hp -= damage

        else:
            print("Invalid choice.")
            continue

        if enemy.hp > 0:
            enemy_damage = enemy.attack
            if enemy.has_bleed_enchantment and random.random() < 0.1:
                print("You are inflicted with bleed!")
                for _ in range(3):
                    player.hp -= 3
                    print("You bleed for 3 damage.")
            player.hp -= enemy_damage
            print(f"The {enemy.name} attacks for {enemy_damage} damage!")

        if bleed_turns > 0:
            enemy.hp -= 5
            print("Enemy suffers 5 bleed damage.")
            bleed_turns -= 1

    if player.hp > 0:
        print(f"\nYou defeated the {enemy.name}!")
        player.xp += enemy.xp_reward
        print(f"You gained {enemy.xp_reward} XP!")
        # Check for rare drops
        maybe_drop_breakthrough_pill(enemy, player)
        if player.xp >= player.level * 100:
            level_up(player)
        check_quests(player, "kill")
    else:
        print("\nYou have fallen in battle.")

def group_battle(players, enemy):
    print(f"\nA wild {enemy.name} appears! All players must fight together!")

    bleed_turns = 0
    while enemy.hp > 0 and any(p.hp > 0 for p in players):
        print(f"\n{enemy.name}: {enemy.hp} HP")
        for p in players:
            if p.hp <= 0:
                continue
            print(f"\n{p.name}: {p.hp} HP", end='')
            # Show resource (Mana or Qi)
            if getattr(p, 'max_qi', 0) > 0:
                print(f", Qi: {getattr(p, 'qi', 0)}/{getattr(p, 'max_qi', 0)}")
            elif p.role in ("Mage", "Warlock") or p.max_mana > 0:
                print(f", Mana: {p.mana}/{p.max_mana}")
            else:
                print()

            while True:
                choice = input(f"{p.name}'s turn - (1) Attack  (2) Inventory  (3) Skill: ").strip()
                if choice == '1':
                    # Dynamic spell menu for Mage/Warlock!
                    if p.role in SPELLS:
                        spell_choice = input("Cast spell? (y) Yes or (n) Normal Attack: ").strip().lower()
                        if spell_choice == 'y':
                            spell = cast_spell_menu(p)
                            if not spell:
                                # cancelled
                                pass
                            else:
                                if spell["effect"] == "fireball":
                                    damage = p.spell_power + p.attack
                                    if spell.get("cost_type") == "mana":
                                        p.mana -= spell.get("cost", 0)
                                    elif spell.get("cost_type") == "qi":
                                        p.qi -= spell.get("cost", 0)
                                    print(f"{p.name} casts Fireball for {damage} damage!")
                                
                                
                                
                                
                                
                                elif spell["effect"] in ("firestorm", "shadow_nova"):
                                    # AoE spells in single-enemy group combat are powerful single-target strikes
                                    damage = p.spell_power + p.attack + 10
                                    if spell.get("cost_type") == "mana":
                                        p.mana -= spell.get("cost", 0)
                                    elif spell.get("cost_type") == "qi":
                                        p.qi -= spell.get("cost", 0)
                                    print(f"{p.name} unleashes {spell['name']} for {damage} damage!")
                                elif spell["effect"] == "eldritch_blast":
                                    damage = p.spell_power + p.attack + random.randint(1,5)
                                    if spell.get("cost_type") == "mana":
                                        p.mana -= spell.get("cost", 0)
                                    elif spell.get("cost_type") == "qi":
                                        p.qi -= spell.get("cost", 0)
                                    print(f"{p.name} casts Eldritch Blast for {damage} damage!")
                                elif spell["effect"] == "hellfire":
                                    damage = p.spell_power + p.attack + 15
                                    p.hp -= spell.get("cost", 0)
                                    print(f"{p.name} uses Hellfire for {damage} damage at the cost of HP!")
                                else:
                                    damage = p.attack
                        else:
                            damage = p.attack
                            print(f"{p.name} attacks for {damage} damage!")
                    else:
                        damage = p.attack
                        print(f"{p.name} attacks for {damage} damage!")

                    if random.randint(1, 100) <= p.bleed_chance:
                        bleed_turns = 3
                        print("Bleed applied!")

                    enemy.hp -= damage
                    break  # Turn complete

                elif choice == '2':
                    used = manage_inventory(p, players, in_battle=True)
                    if used:
                        break  # Turn used
                    else:
                        continue  # Let them act again

                elif choice == '3':
                    skill = use_skill_menu(p)
                    if not skill:
                        continue
                    if skill['effect'] == 'cleave':
                        damage = p.attack + skill.get('power', 0)
                        print(f"{p.name} uses {skill['name']} for {damage} damage!")
                    elif skill['effect'] == 'flowing_palm':
                        damage = p.spell_power + p.attack + skill.get('power', 0)
                        print(f"{p.name} uses {skill['name']} for {damage} Qi damage!")
                    elif skill['effect'] == 'whirlwind':
                        damage = p.attack + skill.get('power', 0) + 6
                        print(f"{p.name} spins in a Whirlwind and strikes for {damage} damage!")
                    elif skill['effect'] == 'qi_wave':
                        cost = skill.get('qi_cost', 0)
                        if getattr(p, 'qi', 0) < cost:
                            print(f"{p.name} doesn't have enough Qi for {skill['name']}!")
                            continue
                        p.qi -= cost
                        damage = p.spell_power + p.attack + skill.get('power', 0)
                        print(f"{p.name} releases a Qi Wave for {damage} damage! (cost {cost} Qi)")
                    elif skill['effect'] == 'overcharge':
                        cost = skill.get('mana_cost', skill.get('qi_cost', 0))
                        if skill.get('qi_cost') is not None or p.role == 'Cultivator':
                            if getattr(p, 'qi', 0) < cost:
                                print(f"{p.name} doesn't have enough Qi for {skill['name']}!")
                                continue
                            p.qi -= cost
                            cost_label = 'Qi'
                        else:
                            if getattr(p, 'mana', 0) < cost:
                                print(f"{p.name} doesn't have enough mana for {skill['name']}!")
                                continue
                            p.mana -= cost
                            cost_label = 'mana'
                        damage = p.attack + skill.get('power', 0) + p.spell_power
                        print(f"{p.name} overcharges and deals {damage} damage (cost {cost} {cost_label})!")
                    elif skill['effect'] == 'berserk':
                        damage = p.attack + skill.get('power', 0)
                        self_cost = skill.get('self_hp_cost', 0)
                        p.hp = max(1, p.hp - self_cost)
                        print(f"{p.name} goes berserk! {skill['name']} deals {damage} damage but costs {self_cost} HP.")
                    else:
                        damage = p.attack
                        print(f"{p.name} uses {skill['name']} for {damage} damage!")

                    p.skill_cooldowns[skill['name']] = skill.get('cooldown', 1)
                    enemy.hp -= damage
                    break

                else:
                    print("Invalid choice.")

            if enemy.hp <= 0:
                break

        if enemy.hp > 0:
            target = random.choice([p for p in players if p.hp > 0])
            damage = enemy.attack
            target.hp -= damage
            print(f"\nThe {enemy.name} attacks {target.name} for {damage} damage!")

            if enemy.has_bleed_enchantment and random.random() < 0.1:
                print(f"{target.name} is bleeding!")
                for _ in range(3):
                    target.hp -= 3
                    print(f"{target.name} bleeds for 3 damage.")

            if bleed_turns > 0:
                enemy.hp -= 5
                print("Enemy suffers 5 bleed damage.")
                bleed_turns -= 1

    if enemy.hp <= 0:
        print(f"\nThe {enemy.name} is defeated!")
        for p in players:
            if p.hp > 0:
                p.xp += enemy.xp_reward
                print(f"{p.name} gains {enemy.xp_reward} XP!")
                if p.xp >= p.level * 100:
                    level_up(p)
                check_quests(p, "kill")
                # Check for rare drops for each participating player
                maybe_drop_breakthrough_pill(enemy, p)
    else:
        print("\nThe party has been defeated.")

def multi_enemy_battle(players, enemies):
    """
    Handles battles where players face multiple enemies.
    `players` is a list of Player objects (one or more).
    `enemies` is a list of Enemy objects.
    Players may attempt to escape during the encounter (chance depends on number of enemies and player level).
    """
    print(f"\nAmbush! {len(enemies)} enemies appear!")

    # Show enemies
    for idx, e in enumerate(enemies, 1):
        print(f" {idx}. {e.name} - {e.hp} HP")

    # Offer an initial escape attempt (by lead player)
    lead = players[0]
    try_escape = input("Attempt to escape before fighting? (y/n): ").strip().lower()
    def calc_escape_chance(player):
        base = 60
        penalty = 10 * (len(enemies) - 1)
        level_bonus = player.level * 2
        chance = max(10, base - penalty + level_bonus)
        return chance

    if try_escape == 'y':
        chance = calc_escape_chance(lead)
        roll = random.randint(1, 100)
        if roll <= chance:
            print(f"You successfully escaped! (rolled {roll} <= {chance})")
            return
        else:
            print(f"Escape failed! (rolled {roll} > {chance}) The enemies block your path and strike first!")
            # enemies get a free round of attacks
            for e in enemies:
                if e.hp <= 0:
                    continue
                target = random.choice([p for p in players if p.hp > 0])
                dmg = e.attack
                target.hp -= dmg
                print(f"{e.name} hits {target.name} for {dmg} damage!")

    # Keep a copy of the original enemies for drop checks later
    all_enemies = [Enemy(e.name, e.hp, e.attack, e.xp_reward, e.has_bleed_enchantment) for e in enemies]

    # Main loop
    while any(e.hp > 0 for e in enemies) and any(p.hp > 0 for p in players):
        # Players' turns
        for p in players:
            if p.hp <= 0:
                continue
            print(f"\n{p.name}: {p.hp} HP")
            # Show resource (Mana or Qi)
            if getattr(p, 'max_qi', 0) > 0:
                print(f"Qi: {getattr(p, 'qi', 0)}/{getattr(p, 'max_qi', 0)}")
            elif p.max_mana > 0:
                print(f"Mana: {p.mana}/{p.max_mana}")
            print("Enemies:")
            for idx, e in enumerate(enemies, 1):
                if e.hp > 0:
                    print(f" {idx}. {e.name} - {e.hp} HP")

            choice = input("Choose action: (1) Attack  (2) Use Inventory  (3) Use Skill  (4) Attempt Escape: ").strip()

            if choice == '1':
                # Choose target enemy
                alive_enemies = [e for e in enemies if e.hp > 0]
                for idx, e in enumerate(alive_enemies, 1):
                    print(f"{idx}. {e.name} - {e.hp} HP")
                t_choice = input("Choose enemy target: ").strip()
                try:
                    target = alive_enemies[int(t_choice) - 1]
                except:
                    print("Invalid target.")
                    continue

                # Spell support for Mage/Warlock
                if p.role in SPELLS:
                    spell_choice = input("Cast spell? (y) Yes or (n) Normal Attack: ").strip().lower()
                    if spell_choice == 'y':
                        spell = cast_spell_menu(p)
                        if spell:
                            if spell["effect"] == "fireball":
                                damage = p.spell_power + p.attack
                                if spell.get("cost_type") == "mana":
                                    p.mana -= spell.get("cost", 0)
                                elif spell.get("cost_type") == "qi":
                                    p.qi -= spell.get("cost", 0)
                                print(f"{p.name} casts Fireball for {damage} damage on {target.name}!")
                            elif spell["effect"] == "qi_strike":
                                damage = p.spell_power + p.attack
                                if spell.get("cost_type") == "mana":
                                    p.mana -= spell.get("cost", 0)
                                elif spell.get("cost_type") == "qi":
                                    p.qi -= spell.get("cost", 0)
                                print(f"{p.name} channels Qi and strikes {target.name} for {damage} damage!")
                            elif spell["effect"] in ("firestorm", "shadow_nova"):
                                # AoE spell: hits all alive enemies
                                cost_type = spell.get("cost_type")
                                cost_amt = spell.get("cost", 0)
                                if cost_type == "mana":
                                    if getattr(p, 'mana', 0) < cost_amt:
                                        print(f"{p.name} doesn't have enough mana for {spell['name']}!")
                                        damage = 0
                                        # skip applying
                                    else:
                                        p.mana -= cost_amt
                                elif cost_type == "qi":
                                    if getattr(p, 'qi', 0) < cost_amt:
                                        print(f"{p.name} doesn't have enough Qi for {spell['name']}!")
                                        damage = 0
                                    else:
                                        p.qi -= cost_amt
                                # Apply to each alive enemy
                                alive_enemies = [e for e in enemies if e.hp > 0]
                                if alive_enemies:
                                    base_dmg = p.spell_power + p.attack + 6
                                    print(f"{p.name} unleashes {spell['name']} hitting {len(alive_enemies)} enemies!")
                                    for ae in alive_enemies:
                                        ae.hp -= base_dmg
                                        print(f"  {ae.name} takes {base_dmg} damage!")
                                    # mark damage applied
                                    damage = 0
                            elif spell["effect"] == "eldritch_blast":
                                damage = p.spell_power + p.attack + random.randint(1,5)
                                if spell.get("cost_type") == "mana":
                                    p.mana -= spell.get("cost", 0)
                                elif spell.get("cost_type") == "qi":
                                    p.qi -= spell.get("cost", 0)
                                print(f"{p.name} casts Eldritch Blast for {damage} damage on {target.name}!")
                            elif spell["effect"] == "hellfire":
                                damage = p.spell_power + p.attack + 15
                                p.hp -= spell.get("cost", 0)
                                print(f"{p.name} uses Hellfire for {damage} damage on {target.name} at the cost of HP!")
                            else:
                                damage = p.attack
                        else:
                            damage = p.attack
                            print(f"{p.name} attacks {target.name} for {damage} damage!")
                    else:
                        damage = p.attack
                        print(f"{p.name} attacks {target.name} for {damage} damage!")
                else:
                    damage = p.attack
                    print(f"{p.name} attacks {target.name} for {damage} damage!")

                if random.randint(1, 100) <= p.bleed_chance:
                    print("Bleed applied to the enemy!")
                    target.hp -= 5  # small bleed instant

                target.hp -= damage

            elif choice == '2':
                used = manage_inventory(p, players, in_battle=True)
                if not used:
                    continue

            elif choice == '3':
                skill = use_skill_menu(p)
                if not skill:
                    continue
                # Target skill effects at a single enemy for simplicity
                alive_enemies = [e for e in enemies if e.hp > 0]
                if not alive_enemies:
                    continue
                target = alive_enemies[0]
                if skill['effect'] == 'cleave':
                    # Cleave deals extra damage and hits one additional enemy if present
                    damage = p.attack + skill.get('power', 0)
                    print(f"{p.name} uses {skill['name']} for {damage} damage on {target.name}!")
                    target.hp -= damage
                    # Hit a second enemy if exists
                    others = [e for e in enemies if e.hp > 0 and e is not target]
                    if others:
                        splash = others[0]
                        splash_dmg = max(1, damage // 2)
                        splash.hp -= splash_dmg
                        print(f"{skill['name']} also hits {splash.name} for {splash_dmg} damage!")
                elif skill['effect'] == 'whirlwind':
                    # Hit all enemies for moderate damage
                    damage = p.attack + skill.get('power', 0)
                    alive_enemies = [e for e in enemies if e.hp > 0]
                    print(f"{p.name} spins in a Whirlwind and hits {len(alive_enemies)} enemies for {damage} damage each!")
                    for ae in alive_enemies:
                        ae.hp -= damage
                elif skill['effect'] == 'qi_wave':
                    cost = skill.get('qi_cost', 0)
                    if getattr(p, 'qi', 0) < cost:
                        print(f"{p.name} doesn't have enough Qi for {skill['name']}!")
                        continue
                    p.qi -= cost
                    damage = p.spell_power + p.attack + skill.get('power', 0)
                    alive_enemies = [e for e in enemies if e.hp > 0]
                    print(f"{p.name} releases a Qi Wave hitting {len(alive_enemies)} enemies for {damage} damage each! (cost {cost} Qi)")
                    for ae in alive_enemies:
                        ae.hp -= damage
                elif skill['effect'] == 'flowing_palm':
                    damage = p.spell_power + p.attack + skill.get('power', 0)
                    print(f"{p.name} uses {skill['name']} for {damage} Qi damage on {target.name}!")
                    target.hp -= damage
                elif skill['effect'] == 'overcharge':
                    cost = skill.get('mana_cost', skill.get('qi_cost', 0))
                    if skill.get('qi_cost') is not None or p.role == 'Cultivator':
                        if getattr(p, 'qi', 0) < cost:
                            print(f"{p.name} doesn't have enough Qi for {skill['name']}!")
                            continue
                        p.qi -= cost
                        cost_label = 'Qi'
                    else:
                        if getattr(p, 'mana', 0) < cost:
                            print(f"{p.name} doesn't have enough mana for {skill['name']}!")
                            continue
                        p.mana -= cost
                        cost_label = 'mana'
                    damage = p.attack + skill.get('power', 0) + p.spell_power
                    print(f"{p.name} overcharges and deals {damage} damage (cost {cost} {cost_label}) on {target.name}!")
                elif skill['effect'] == 'berserk':
                    damage = p.attack + skill.get('power', 0)
                    self_cost = skill.get('self_hp_cost', 0)
                    p.hp = max(1, p.hp - self_cost)
                    print(f"{p.name} goes berserk! {skill['name']} deals {damage} damage but costs {self_cost} HP.")
                    target.hp -= damage
                else:
                    damage = p.attack
                    print(f"{p.name} uses {skill['name']} for {damage} damage on {target.name}!")
                    target.hp -= damage

                p.skill_cooldowns[skill['name']] = skill.get('cooldown', 1)

            elif choice == '4':
                # Attempt to escape mid-battle
                chance = calc_escape_chance(p)
                roll = random.randint(1, 100)
                if roll <= chance:
                    print(f"{p.name} successfully escaped the battle! (rolled {roll} <= {chance})")
                    return
                else:
                    print(f"{p.name} failed to escape (rolled {roll} > {chance}).")
                    # continue; enemies will act next

            else:
                print("Invalid choice.")
                continue

            # Remove defeated enemies quietly
            enemies = [e for e in enemies if e.hp > 0]
            if not enemies:
                break

        # Enemies' turn
        if enemies and any(p.hp > 0 for p in players):
            for e in enemies:
                if e.hp <= 0:
                    continue
                target = random.choice([p for p in players if p.hp > 0])
                dmg = e.attack
                target.hp -= dmg
                print(f"\n{e.name} attacks {target.name} for {dmg} damage!")

    # Outcome
    if not any(e.hp > 0 for e in enemies):
        print("\nYou defeated all enemies!")
        total_xp = sum(e.xp_reward for e in enemies)
        for p in players:
            if p.hp > 0:
                p.xp += total_xp
                print(f"{p.name} gains {total_xp} XP!")
                if p.xp >= p.level * 100:
                    level_up(p)
                check_quests(p, "kill")
                # Check for rare drops against the original enemies
                for orig in all_enemies:
                    maybe_drop_breakthrough_pill(orig, p)
    else:
        print("\nYour party was defeated by the ambush.")

# -------------------------------
# Level Up System
# -------------------------------
def level_up(player):
    player.level += 1
    player.stat_points += 3
    player.max_hp += 10
    player.hp = player.max_hp

    # Default linear gains for non-cultivators
    if player.role != "Cultivator":
        player.attack += 2
        if player.role == "Mage":
            player.max_mana += 10
            player.mana = player.max_mana
            player.spell_power += 2
        if player.role == "Warlock":
            player.max_mana += 5
            player.mana = player.max_mana
            player.hp += 5
            player.spell_power += 2
        print(f"\n*** {player.name} leveled up to {player.level}! Stat points +3 ***")
        return

    # Cultivator: exponential scaling and realm breakthroughs
    # Use base stats as the source of truth and compute scaled stats
    # growth per level (exponential)
    growth = 1.12
    # Recompute attack and spell_power from base values
    player.attack = max(1, int(player.base_attack * (growth ** (player.level - 1))))
    player.spell_power = max(0, int(player.base_spell_power * (growth ** (player.level - 1))))

    # Increase Qi pool slightly each level (base per-level Qi gain)
    player.max_qi += 10
    player.qi = player.max_qi

    # Check for realm breakthroughs (data-driven) but require a Breakthrough Pill to advance
    # If the cultivator has a Breakthrough Pill in inventory it will be consumed automatically
    # and the breakthrough applied. Otherwise, inform the player that a pill is required.
    while player.realm_stage + 1 < len(CULTIVATOR_REALMS):
        next_realm = CULTIVATOR_REALMS[player.realm_stage + 1]
        if player.level >= next_realm.get("level_req", 9999):
            # attempt to break through; this will consume a pill if present
            success = attempt_realm_breakthrough(player, consume_pill=True)
            if not success:
                print(f"You meet the level requirement for {next_realm.get('name')}, but you need a Breakthrough Pill to advance.")
                break
            # if success, the loop continues and may attempt the next realm too
        else:
            break
    # If no realm advancement occurred this level, still show a general message
    if player.realm_stage < 0 or not CULTIVATOR_REALMS:
        print(f"\n*** {player.name} advanced to level {player.level} of cultivation! Stat points +3 ***")

# -------------------------------
# Inventory
# -------------------------------

def manage_inventory(player, players, in_battle=False):
    used = False

    if not player.inventory:
        print("\nYour inventory is empty.")
        input("Press Enter to continue...")
        return used

    print("\n==== Inventory ====")
    for idx, item in enumerate(player.inventory, 1):
        print(f"{idx}. {item}")
    choice = input("Choose item to use (or press Enter to cancel): ").strip()

    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(player.inventory):
        print("Cancelled or invalid choice.")
        return used

    item = player.inventory[int(choice) - 1]

    if item == "Health Potion":
        if player.hp < player.max_hp:
            heal = min(30, player.max_hp - player.hp)
            player.hp += heal
            print(f"You used a Health Potion and restored {heal} HP!")
            used = True
        else:
            print("Your HP is already full.")

    elif item == "Mana Potion" and player.role == "Mage":
        if player.mana < player.max_mana:
            regen = min(30, player.max_mana - player.mana)
            player.mana += regen
            print(f"You used a Mana Potion and restored {regen} MP!")
            used = True
        else:
            print("Your Mana is already full.")

    elif item == "Qi Potion" and player.role == "Cultivator":
        if getattr(player, 'qi', 0) < getattr(player, 'max_qi', 0):
            regen = min(40, getattr(player, 'max_qi', 0) - getattr(player, 'qi', 0))
            player.qi = getattr(player, 'qi', 0) + regen
            print(f"You used a Qi Potion and restored {regen} Qi!")
            used = True
        else:
            print("Your Qi is already full.")

    elif item == "Magic Scroll" and player.role == "Mage":
        print("The Magic Scroll glows... You feel wiser!")
        player.spell_power += 1
        used = True

    elif item == "Steel Sword":
        print("You equip the Steel Sword. Attack +2!")
        player.attack += 2
        used = True

    elif item == "Bleed Enchantment":
        print("Your weapon gains a bleeding edge! Bleed chance +10%.")
        player.bleed_chance += 10
        used = True

    elif item == "Phoenix Feather":
        unconscious_allies = [p for p in players if p != player and p.hp <= 0]
        if not unconscious_allies:
            print("No teammates to revive.")
            return used  # Don’t consume turn or item
        else:
            for idx, p in enumerate(unconscious_allies, 1):
                print(f"{idx}. {p.name}")
            choice = input("Choose a teammate to revive: ").strip()
            try:
                revived = unconscious_allies[int(choice) - 1]
                revived.hp = revived.max_hp // 2
                print(f"{revived.name} has been revived with {revived.hp} HP!")
                used = True
            except:
                print("Invalid choice. Feather not used.")
                return used  # Don't consume turn or item if error

    elif item == "Breakthrough Pill":
        # Only useful for Cultivators and only if they meet the realm requirement
        if player.role != "Cultivator":
            print("Only Cultivators can use a Breakthrough Pill.")
            return used

        # Attempt breakthrough and only consume if success
        success = attempt_realm_breakthrough(player, consume_pill=True)
        if success:
            used = True
            # Complete any quests that require this item and for which the player already met the level requirement
            for quest in player.quests:
                if quest.get('completed'):
                    continue
                if quest.get('requires_item') == 'Breakthrough Pill' and quest['type'] == 'level' and player.level >= quest.get('goal', 0):
                    quest['completed'] = True
                    # grant reward
                    reward = quest.get('reward')
                    if reward:
                        player.inventory.append(reward)
                        print(f"\nQuest Complete: {quest['name']}! You received a {reward}!")
        else:
            print("The Breakthrough Pill had no effect. Perhaps you're not high enough level or another pill is required.")
            used = False

    else:
        print(f"You can't use the {item} right now.")

    if used:
        player.inventory.pop(int(choice) - 1)

    input("Press Enter to continue...")
    return used

# -------------------------------
# Save/Load Functions
# -------------------------------
def save_multiplayer_game(players, filename="autosave", silent=False, timestamp=False, keep_latest=5):
    if timestamp:
        import datetime
        time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename_full = f"{filename}_{time_str}"
    else:
        filename_full = filename

    filepath = f"{filename_full}.json"

    with open(filepath, "w") as f:
        json.dump([p.__dict__ for p in players], f)

    if not silent:
        print(f"Game saved as {filepath}")

    # --- Limit autosaves to latest `keep_latest` files ---
    if timestamp:
        pattern = f"{filename}_"
        files = sorted(
            [f for f in os.listdir() if f.startswith(pattern) and f.endswith(".json")],
            key=os.path.getmtime,
            reverse=True
        )

        for old_file in files[keep_latest:]:
            os.remove(old_file)

def load_multiplayer_game():
    saves = [f for f in os.listdir() if f.endswith(".json")]
    if not saves:
        print("No save files found.")
        return []

    print("\nAvailable save files:")
    for idx, file in enumerate(saves):
        print(f"{idx + 1}. {file}")
    choice = input("Enter the number of the save to load: ").strip()

    try:
        filepath = saves[int(choice) - 1]
        with open(filepath, "r") as f:
            raw_players = json.load(f)

        players = []
        for pdata in raw_players:
            player = Player(pdata["name"], pdata.get("role", "Warrior"))
            player.__dict__.update(pdata)
            assign_quests(player)
            players.append(player)

        print(f"Loaded {len(players)} player(s).")
        return players
    except:
        print("Failed to load game.")
        return []

def cleanup_old_autosaves(base_name="autosave", keep_latest=1):
    files = sorted(
        [f for f in os.listdir() if f.startswith(base_name + "_") and f.endswith(".json")],
        key=os.path.getmtime,
        reverse=True
    )
    for old_file in files[keep_latest:]:
        try:
            os.remove(old_file)
            print(f"Deleted old autosave: {old_file}")
        except Exception as e:
            print(f"Failed to delete {old_file}: {e}")

def delete_save_file(protect_latest=True, base_name="autosave"):
    saves = [f for f in os.listdir() if f.endswith(".json")]
    if not saves:
        print("No save files to delete.")
        return

    # Identify the latest autosave (if protection is enabled)
    latest_autosave = None
    if protect_latest:
        autosaves = [f for f in saves if f.startswith(base_name + "_")]
        if autosaves:
            latest_autosave = max(autosaves, key=os.path.getmtime)

    while True:
        print("\n==== Delete Save Files ====")
        for idx, file in enumerate(saves, 1):
            tag = " (LATEST AUTOSAVE)" if protect_latest and file == latest_autosave else ""
            print(f"{idx}. {file}{tag}")
        print("a. Delete all (except latest autosave)" if protect_latest else "a. Delete all")
        print("q. Cancel")

        choice = input("Choose a save to delete (by number), 'a' to delete all, or 'q' to cancel: ").strip().lower()

        if choice == 'q':
            print("Cancelled.")
            return
        elif choice == 'a':
            confirm = input("Are you sure you want to delete all save files" +
                            (" except the latest autosave" if protect_latest else "") +
                            "? (y/n): ").strip().lower()
            if confirm == 'y':
                deleted = 0
                for file in saves:
                    if protect_latest and file == latest_autosave:
                        continue
                    try:
                        os.remove(file)
                        deleted += 1
                    except Exception as e:
                        print(f"Failed to delete {file}: {e}")
                print(f"Deleted {deleted} save file(s).")
            else:
                print("Bulk deletion cancelled.")
            return
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(saves):
                filename = saves[idx]
                if protect_latest and filename == latest_autosave:
                    print("⚠ You cannot delete the latest autosave.")
                    continue
                confirm = input(f"Are you sure you want to delete '{filename}'? (y/n): ").strip().lower()
                if confirm == 'y':
                    try:
                        os.remove(filename)
                        print(f"Deleted {filename}")
                        saves.remove(filename)
                        if filename == latest_autosave:
                            latest_autosave = None
                    except Exception as e:
                        print(f"Error deleting file: {e}")
                else:
                    print("Deletion cancelled.")
            else:
                print("Invalid selection.")
        else:
            print("Invalid input.")

# -------------------------------
# Shop Function
# -------------------------------
def shop(player):
    print("\n==== Welcome to the Shop ====")

    # Define item prices
    all_items = {
        "Health Potion": 20,
        "Mana Potion": 25,
        "Qi Potion": 30,
        "Magic Scroll": 40,
        "Steel Sword": 50,
        "Bleed Enchantment": 60,
        "Phoenix Feather": 150,  # Rare item for reviving teammates
        "Breakthrough Pill": 300
    }

    # Weighted item pool for rarity
    weighted_pool = (
        ["Health Potion"] * 5 +
        ["Mana Potion"] * 4 +
        ["Qi Potion"] * 3 +
        ["Magic Scroll"] * 3 +
        ["Steel Sword"] * 2 +
        ["Bleed Enchantment"] * 2 +
        ["Breakthrough Pill"] * 1 +
        ["Phoenix Feather"] * 1  # Rare
    )

    # Choose 3 to 5 unique items randomly
    stock_keys = random.sample(list(set(weighted_pool)), random.randint(3, 5))

    # Assign random stock quantities (1–3 for each item)
    shop_stock = {item: {"price": all_items[item], "stock": random.randint(1, 3)} for item in stock_keys}

    while True:
        print("\nAvailable Items:")
        for idx, (item, data) in enumerate(shop_stock.items(), 1):
            rare = " (Rare!)" if item == "Phoenix Feather" else ""
            print(f"{idx}. {item} - {data['price']} gold (Stock: {data['stock']}){rare}")
        print("0. Leave Shop")

        choice = input("Choose an item to buy or 0 to exit: ").strip()
        if choice == "0":
            print("You leave the shop.")
            break

        try:
            idx = int(choice) - 1
            item = list(shop_stock.keys())[idx]
            data = shop_stock[item]

            if player.gold >= data["price"]:
                if data["stock"] > 0:
                    player.gold -= data["price"]
                    player.inventory.append(item)
                    shop_stock[item]["stock"] -= 1
                    print(f"You bought a {item}!")
                    # If buying a Breakthrough Pill and player already meets any quest requirements, auto-apply
                    if item == "Breakthrough Pill" and player.role == "Cultivator":
                        for quest in player.quests:
                            if quest.get('completed'):
                                continue
                            if quest.get('requires_item') == 'Breakthrough Pill' and quest['type'] == 'level' and player.level >= quest.get('goal', 0):
                                print("You acquired a Breakthrough Pill and meet the level requirement — it will be consumed to complete your trial.")
                                # attempt breakthrough (will consume pill)
                                attempt_realm_breakthrough(player, consume_pill=True)
                                quest['completed'] = True
                                reward = quest.get('reward')
                                if reward:
                                    player.inventory.append(reward)
                                    print(f"\nQuest Complete: {quest['name']}! You received a {reward}!")
                    if shop_stock[item]["stock"] == 0:
                        print(f"{item} is now out of stock.")
                else:
                    print(f"{item} is out of stock.")
            else:
                print("You don't have enough gold.")
        except (IndexError, ValueError):
            print("Invalid selection.")

# -------------------------------
# Main Menu
# -------------------------------

def main_menu(player, players):
    menu = [
        ("Explore", lambda p: explore(p, players)),
        ("Check Status", lambda p: (p.show_status(), input("Press Enter to continue..."))),
        ("Use Inventory", lambda p: manage_inventory(p, players, in_battle=False)),
        ("Allocate Stats", allocate_stats),
        ("Revive Teammate", lambda p: revive_teammate(p, players)),
        ("Save Game", lambda p: save_multiplayer_game(players)),
        ("Quit Game", lambda p: "quit"),
        ("View Quests", show_quests),
        ("Visit Shop", shop),
        ("Delete Save File", lambda p: delete_save_file())
    ]

    if len(players) >= 2:
        menu.append(("Trade with another player", lambda p: trade_items(p, players)))

    print(f"\n--- {player.name}'s Turn ---")
    for i, (label, _) in enumerate(menu, 1):
        print(f"{i}. {label}")

    choice = input(f"Choose an option (1-{len(menu)}): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(menu)):
        print("Invalid choice.")
        return None  # Turn will repeat

    label, action = menu[int(choice) - 1]
    result = action(player)
    return result

# -------------------------------
# Player Interaction
# -------------------------------

def trade_items(player, players):
    others = [p for p in players if p != player and p.hp > 0]
    if not others:
        print("No other players are available for trading.")
        return

    print("\nAvailable players to trade with:")
    for idx, p in enumerate(others, 1):
        print(f"{idx}. {p.name}")

    choice = input("Choose a player to trade with (or press Enter to cancel): ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(others):
        print("Cancelled.")
        return

    target = others[int(choice) - 1]
    if not player.inventory:
        print("You have nothing to trade.")
        return

    print("\nYour inventory:")
    for idx, item in enumerate(player.inventory, 1):
        print(f"{idx}. {item}")
    item_choice = input("Choose an item to give: ").strip()
    try:
        item = player.inventory.pop(int(item_choice) - 1)
        target.inventory.append(item)
        print(f"You gave {item} to {target.name}.")
    except:
        print("Invalid choice.")

def revive_teammate(current_player, players):
    unconscious_allies = [p for p in players if p != current_player and p.hp <= 0]
    if not unconscious_allies:
        print("\nNo teammates need reviving.")
        input("Press Enter to continue...")
        return

    print("\nUnconscious teammates:")
    for idx, ally in enumerate(unconscious_allies, 1):
        print(f"{idx}. {ally.name}")

    choice = input("Choose a teammate to revive (or press Enter to cancel): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(unconscious_allies)):
        print("Cancelled.")
        return

    ally = unconscious_allies[int(choice) - 1]

    if "Phoenix Feather" in current_player.inventory:
        current_player.inventory.remove("Phoenix Feather")
        ally.hp = int(ally.max_hp * 0.5)
        print(f"\nYou used a Phoenix Feather to revive {ally.name} with {ally.hp} HP!")
    else:
        print("You need a Phoenix Feather to revive someone.")
    
    input("Press Enter to continue...")

# -------------------------------
# Main Game Loop
# -------------------------------
def main():
    print("===========")
    print(" Welcome!")
    print("===========\n")

    players = []
    save_name = "autosave"  # Default

    # Check if there are any save files
    if any(f.endswith(".json") for f in os.listdir()):
        if input("A saved game was found. Load it? (y/n): ").strip().lower() == 'y':
            players = load_multiplayer_game()
            if players:
                save_name = input("Name this session for future saves: ").strip() or "autosave"

    # If no players were loaded, create new game
    if not players:
        num_players = input("How many players? (1-4): ").strip()
        try:
            num_players = max(1, min(4, int(num_players)))
        except:
            num_players = 1

        for i in range(num_players):
            print("\nChoose your class:")
            for idx, class_name in enumerate(CLASS_DEFS.keys(), 1):
                print(f"{idx}. {class_name}")
            role_choice = input(f"Player {i + 1}, enter the number for your chosen class (default is 1): ").strip()
            if role_choice.isdigit() and 1 <= int(role_choice) <= len(CLASS_DEFS):
                role = list(CLASS_DEFS.keys())[int(role_choice) - 1]
            else:
                role = list(CLASS_DEFS.keys())[0]
            # If the developer-only class was chosen, require the developer password
            if role == "Cultivator":
                pwd = input("Developer class selected. Enter developer password to unlock (leave blank to cancel): ").strip()
                if not pwd or pwd != DEV_PASSWORD:
                    print("Access denied or cancelled. Defaulting to Warrior.")
                    role = list(CLASS_DEFS.keys())[0]
        name = input(f"Enter name for Player {i + 1}: ").strip()
        player = Player(name, role)
        assign_quests(player)
        players.append(player)

        save_name = input("Name your save file: ").strip() or "autosave"

    # Game loop starts here
    turn = 0
    while any(p.hp > 0 for p in players):
        player = players[turn]

        # Decrement skill cooldowns for the active player at the start of their turn
        if hasattr(player, 'skill_cooldowns'):
            for s in list(player.skill_cooldowns.keys()):
                if player.skill_cooldowns[s] > 0:
                    player.skill_cooldowns[s] -= 1
                    if player.skill_cooldowns[s] == 0:
                        print(f"{player.name}'s skill '{s}' is ready!")

        if player.hp <= 0:
            print(f"\n{player.name} is unconscious and skips their turn.")
            turn = (turn + 1) % len(players)
            continue

        if player.role == "Mage":
            player.mana = min(player.max_mana, player.mana + 5)
            print(f"\n({player.name}'s mana regenerates by 5. Mana: {player.mana}/{player.max_mana})")
        elif player.role == "Cultivator":
            player.qi = min(getattr(player, 'max_qi', 0), getattr(player, 'qi', 0) + 5)
            print(f"\n({player.name}'s Qi regenerates by 5. Qi: {getattr(player, 'qi', 0)}/{getattr(player, 'max_qi', 0)})")

        result = main_menu(player, players)

        if result == "quit":
            print("\nThanks for playing!")
            response = input("Do you want to delete all autosaves except the most recent one? (y/n): ").strip().lower()
            if response == 'y':
                cleanup_old_autosaves(base_name=save_name)
            break

        save_multiplayer_game(players, filename=save_name, silent=True, timestamp=True, keep_latest=5)

        turn = (turn + 1) % len(players)

    print("\nGame over! All players have fallen or quit.")

if __name__ == "__main__":
    main()
