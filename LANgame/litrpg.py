PATCH: Adds dynamic spell casting menu and SPELLS database. Refactors battle() logic for cleaner spell choice.

# SPELLS database after imports
SPELLS = {
    "Mage": [
        {
            "name": "Fireball",
            "cost_type": "mana",
            "cost": 10,
            "description": "Deal spell power + attack damage.",
            "effect": "fireball"
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
    ]
}

# Add this helper above battle()
def cast_spell_menu(player):
    available_spells = SPELLS.get(player.role, [])
    if not available_spells:
        print("You have no spells to cast.")
        return None

    print("\nWhich spell would you like to cast?")
    for idx, sp in enumerate(available_spells, 1):
        if sp["cost_type"] == "mana":
            affordable = player.mana >= sp["cost"]
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
        if selected_spell["cost_type"] == "mana" and player.mana < selected_spell["cost"]:
            print("Not enough mana!")
            return None
        if selected_spell["cost_type"] == "hp" and player.hp <= selected_spell["cost"]:
            print("Not enough HP!")
            return None
        return selected_spell
    except:
        print("Invalid input.")
        return None

# Refactor Mage/Warlock battle spell casting inside battle():
# ... inside the action block where you check for class spell
if player.role in SPELLS:
    spell_choice = input("Cast spell? (y) Yes or (n) Normal Attack: ").strip().lower()
    if spell_choice == 'y':
        spell = cast_spell_menu(player)
        if not spell:
            damage = player.attack
            print(f"You attack the {enemy.name} for {damage} damage!")
        elif spell["effect"] == "fireball":
            player.mana -= spell["cost"]
            damage = player.attack + player.spell_power
            print(f"You cast Fireball for {damage} damage!")
        elif spell["effect"] == "eldritch_blast":
            player.mana -= spell["cost"]
            damage = player.attack + player.spell_power + random.randint(1,5)
            print(f"You cast Eldritch Blast for {damage} damage!")
        elif spell["effect"] == "hellfire":
            print(f"You have {player.hp} HP. How much will you sacrifice? (minimum 1, max {player.hp - 1})")
            try:
                max_sac = max(1, player.hp - 1)
                hp_sacrifice = int(input("HP to sacrifice: ").strip())
                if not (1 <= hp_sacrifice <= max_sac):
                    print("Invalid amount.")
                    damage = 0
                else:
                    player.hp -= hp_sacrifice
                    damage = player.attack + player.spell_power + hp_sacrifice + random.randint(1, 5)
                    print(f"You cast Hellfire, sacrificing {hp_sacrifice} HP for {damage} damage!")
            except:
                print("Invalid input.")
                damage = 0
    else:
        damage = player.attack
        print(f"You attack the {enemy.name} for {damage} damage!")
else:
    damage = player.attack
    print(f"You attack the {enemy.name} for {damage} damage!")