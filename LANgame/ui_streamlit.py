import streamlit as st
import random
from litrpg import Player, Enemy, CLASS_DEFS, SKILLS, SPELLS, level_up, check_quests, assign_quests
import os
import json

# Simple Streamlit front-end for the litrpg game (single-player prototype)
# Run with: streamlit run ui_streamlit.py

st.set_page_config(page_title="LitRPG UI", layout="wide")

# Helpers
def init_state():
    if 'player' not in st.session_state:
        st.session_state.player = None
    if 'encounter' not in st.session_state:
        st.session_state.encounter = None
    if 'log' not in st.session_state:
        st.session_state.log = []
    if 'turn' not in st.session_state:
        st.session_state.turn = 'explore'
    if 'skill_cooldowns' not in st.session_state:
        st.session_state.skill_cooldowns = {}


def log(msg):
    st.session_state.log.append(msg)


def reset_encounter():
    st.session_state.encounter = None
    st.session_state.turn = 'explore'


def create_player(name, role):
    p = Player(name, role)
    assign_quests(p)
    # initialize skill cooldowns
    p.skill_cooldowns = {s['name']: 0 for s in p.skill_list}
    st.session_state.player = p
    st.session_state.skill_cooldowns = p.skill_cooldowns
    log(f"Created player {p.name} the {p.role}")


def rerun_safe():
    """Attempt to call st.experimental_rerun() safely from handlers.
    Some Streamlit contexts raise an internal exception when experimental_rerun is called; swallow it.
    """
    try:
        st.experimental_rerun()
    except Exception:
        return

# Combat helpers

def spawn_enemy_tuple(tpl):
    return Enemy(tpl[0], tpl[1], tpl[2], tpl[3], random.random() < 0.03)


def start_explore():
    p = st.session_state.player
    if not p:
        st.warning("Create a player first.")
        return

    r = random.random()
    # multi-enemy chance
    if r < 0.6:
        # enemy encounter
        enemy_pool = [
            ("Goblin", 30, 5, 20), ("Skeleton", 40, 7, 25),
            ("Wolf", 35, 6, 22), ("Bat", 25, 4, 15),
            ("Orc", 50, 10, 30), ("Troll", 60, 12, 40),
            ("Giant", 70, 15, 50)
        ]
        allowed = [e for e in enemy_pool if p.level >= 3 or e[1] < 50]
        if random.random() < 0.2:
            count = random.choice([2,2,3])
            chosen = random.choices(allowed, k=count)
            enemies = [spawn_enemy_tuple(e) for e in chosen]
            st.session_state.encounter = {
                'type': 'multi',
                'enemies': enemies
            }
            st.session_state.turn = 'battle'
            log(f"Ambush! {len(enemies)} enemies appeared.")
        else:
            e = random.choice(allowed)
            enemy = spawn_enemy_tuple(e)
            st.session_state.encounter = {
                'type': 'single',
                'enemies': [enemy]
            }
            st.session_state.turn = 'battle'
            log(f"A wild {enemy.name} appears!")
    elif r < 0.7:
        heal = random.randint(10,30)
        p.hp = min(p.max_hp, p.hp + heal)
        log(f"You found a cache and regained {heal} HP.")
    elif r < 0.8:
        gold = random.randint(10,20)
        p.gold += gold
        log(f"You found {gold} gold.")
    else:
        log("The area is peaceful.")


def apply_player_attack(target_idx=0):
    p = st.session_state.player
    enc = st.session_state.encounter
    enemies = enc['enemies']
    if target_idx < 0 or target_idx >= len(enemies):
        log("Invalid target")
        return
    target = enemies[target_idx]
    dmg = p.attack
    target.hp -= dmg
    log(f"{p.name} attacks {target.name} for {dmg} damage.")
    end_step()


def use_player_skill(skill_name, target_idx=0):
    p = st.session_state.player
    enc = st.session_state.encounter
    enemies = enc['enemies']
    skill = None
    for s in p.skill_list:
        if s['name'] == skill_name:
            skill = s
            break
    if not skill:
        log("Skill not found.")
        return
    if p.skill_cooldowns.get(skill_name, 0) > 0:
        log("Skill is on cooldown.")
        return
    # apply effects for our simple set
    if skill['effect'] == 'cleave':
        if target_idx >= len(enemies):
            log("Invalid target")
            return
        target = enemies[target_idx]
        dmg = p.attack + skill.get('power',0)
        target.hp -= dmg
        log(f"{p.name} uses {skill_name} on {target.name} for {dmg} damage.")
        # splash to another enemy
        others = [e for e in enemies if e.hp>0 and e is not target]
        if others:
            splash = others[0]
            splash_dmg = max(1, dmg//2)
            splash.hp -= splash_dmg
            log(f"{skill_name} also hits {splash.name} for {splash_dmg} damage.")
    elif skill['effect'] == 'berserk':
        if target_idx >= len(enemies):
            log("Invalid target")
            return
        target = enemies[target_idx]
        dmg = p.attack + skill.get('power',0)
        cost = skill.get('self_hp_cost',0)
        p.hp = max(1, p.hp - cost)
        target.hp -= dmg
        log(f"{p.name} goes berserk: deals {dmg} to {target.name} and costs {cost} HP.")
    else:
        log("Skill has no effect implementation.")
        return

    # set cooldown
    p.skill_cooldowns[skill_name] = skill.get('cooldown',1)
    st.session_state.skill_cooldowns = p.skill_cooldowns
    end_step()


def end_step():
    # Remove dead enemies
    enc = st.session_state.encounter
    enemies = [e for e in enc['enemies'] if e.hp > 0]
    enc['enemies'] = enemies
    st.session_state.encounter = enc

    # Enemy turn
    if enemies:
        for e in enemies:
            if e.hp <= 0:
                continue
            p = st.session_state.player
            if p.hp <= 0:
                break
            dmg = e.attack
            p.hp -= dmg
            log(f"{e.name} attacks {p.name} for {dmg} damage.")

    # decrement cooldowns
    p = st.session_state.player
    for sk in list(p.skill_cooldowns.keys()):
        if p.skill_cooldowns[sk] > 0:
            p.skill_cooldowns[sk] -= 1
            if p.skill_cooldowns[sk] == 0:
                log(f"{p.name}'s skill {sk} is ready.")
    st.session_state.skill_cooldowns = p.skill_cooldowns

    # Check end conditions
    if not enc['enemies']:
        # victory
        total_xp = sum(e.xp_reward for e in enc.get('orig_enemies', enc['enemies'])) if 'orig_enemies' in enc else sum(e.xp_reward for e in enc['enemies'])
        # if orig_enemies not saved, award based on remaining final enemies (safe fallback)
        if total_xp == 0:
            total_xp = 10
        p.xp += total_xp
        log(f"You defeated the enemies and gained {total_xp} XP!")
        check_quests(p, 'kill')
        if p.xp >= p.level * 100:
            level_up(p)
        reset_encounter()
        return

    # if player died
    if p.hp <= 0:
        log("You have fallen in battle.")
        reset_encounter()
        return


def attempt_escape():
    p = st.session_state.player
    enc = st.session_state.encounter
    num = len(enc['enemies'])
    base = 60
    penalty = 10 * (num - 1)
    chance = max(10, base - penalty + p.level*2)
    roll = random.randint(1,100)
    if roll <= chance:
        log(f"Escape successful! (rolled {roll} <= {chance})")
        reset_encounter()
    else:
        log(f"Escape failed (rolled {roll} > {chance}). Enemies strike!")
        # enemies get a free hit
        for e in enc['enemies']:
            if e.hp>0:
                dmg = e.attack
                p.hp -= dmg
                log(f"{e.name} hits {p.name} for {dmg} damage.")
        if p.hp <= 0:
            log("You have fallen while trying to escape.")
            reset_encounter()


# -------------------------------
# Additional UI helpers: Inventory, Shop, Save/Load, Allocate Stats, Quests
# -------------------------------

def init_shop():
    if 'shop_stock' not in st.session_state:
        all_items = {
            "Health Potion": 20,
            "Mana Potion": 25,
            "Magic Scroll": 40,
            "Steel Sword": 50,
            "Bleed Enchantment": 60,
            "Phoenix Feather": 150
        }
        weighted_pool = (
            ["Health Potion"] * 5 + ["Mana Potion"] * 4 + ["Magic Scroll"] * 3 +
            ["Steel Sword"] * 2 + ["Bleed Enchantment"] * 2 + ["Phoenix Feather"]
        )
        stock_keys = random.sample(list(set(weighted_pool)), random.randint(3,5))
        st.session_state.shop_stock = {item: {"price": all_items[item], "stock": random.randint(1,3)} for item in stock_keys}


def render_inventory_ui():
    p = st.session_state.player
    if not p:
        return
    st.subheader("Inventory")
    if not p.inventory:
        st.write("(empty)")
        return
    for idx, item in enumerate(list(p.inventory)):
        col_a, col_b = st.columns([3,1])
        with col_a:
            st.write(f"{item}")
        with col_b:
            if st.button(f"Use {item}", key=f"use_{idx}"):
                used = False
                if item == "Health Potion":
                    if p.hp < p.max_hp:
                        heal = min(30, p.max_hp - p.hp)
                        p.hp += heal
                        log(f"You used a Health Potion and restored {heal} HP!")
                        used = True
                    else:
                        log("Your HP is already full.")
                elif item == "Mana Potion" and p.role == "Mage":
                    if p.mana < p.max_mana:
                        regen = min(30, p.max_mana - p.mana)
                        p.mana += regen
                        log(f"You used a Mana Potion and restored {regen} MP!")
                        used = True
                    else:
                        log("Your Mana is already full.")
                elif item == "Magic Scroll" and p.role == "Mage":
                    p.spell_power += 1
                    log("The Magic Scroll glows... Spell Power +1")
                    used = True
                elif item == "Steel Sword":
                    p.attack += 2
                    log("You equip the Steel Sword. Attack +2!")
                    used = True
                elif item == "Bleed Enchantment":
                    p.bleed_chance += 10
                    log("Your weapon gains a bleeding edge! Bleed chance +10%.")
                    used = True
                elif item == "Phoenix Feather":
                    log("Phoenix Feather can only revive allies in multiplayer.")
                else:
                    log(f"Can't use {item} here.")

                if used:
                    try:
                        p.inventory.remove(item)
                    except:
                        pass


def open_shop_ui():
    init_shop()
    stock = st.session_state.shop_stock
    st.subheader("Shop")
    for idx, (name, data) in enumerate(stock.items()):
        col1, col2 = st.columns([3,1])
        with col1:
            rare = " (Rare!)" if name == "Phoenix Feather" else ""
            st.write(f"{name} - {data['price']} gold (Stock: {data['stock']}){rare}")
        with col2:
            if st.button(f"Buy {idx}", key=f"buy_{idx}"):
                p = st.session_state.player
                if p.gold >= data['price'] and data['stock'] > 0:
                    p.gold -= data['price']
                    p.inventory.append(name)
                    stock[name]['stock'] -= 1
                    log(f"You bought a {name}!")
                elif data['stock'] <= 0:
                    log(f"{name} is out of stock.")
                else:
                    log("You don't have enough gold.")


def save_player_file():
    p = st.session_state.player
    if not p:
        st.warning("No player to save.")
        return
    fname = st.text_input("Save filename (without extension)", key='save_name')
    if st.button("Save to file"):
        if not fname:
            st.warning("Enter a filename")
            return
        try:
            from litrpg import save_multiplayer_game
            save_multiplayer_game([p], filename=fname, silent=True, timestamp=False)
            log(f"Player saved to {fname}.json")
        except Exception as e:
            log(f"Failed to save: {e}")


def load_player_file():
    files = [f for f in os.listdir() if f.endswith('.json')]
    if not files:
        st.write("No save files found.")
        return
    choice = st.selectbox("Load file", files, key='load_select')
    if st.button("Load"):
        try:
            with open(choice, 'r') as f:
                raw = json.load(f)
            if isinstance(raw, list) and raw:
                pdata = raw[0]
                p = Player(pdata.get('name','Loaded'), pdata.get('role','Warrior'))
                p.__dict__.update(pdata)
                assign_quests(p)
                st.session_state.player = p
                log(f"Loaded player {p.name} from {choice}")
            else:
                st.write("Invalid save file format.")
        except Exception as e:
            log(f"Failed to load: {e}")


def allocate_stats_ui():
    p = st.session_state.player
    if not p:
        return
    if p.stat_points <= 0:
        st.write("No stat points to allocate.")
        return
    st.subheader("Allocate Stat Points")
    st.write(f"You have {p.stat_points} stat points.")
    opts = p.stat_options
    for idx, opt in enumerate(opts,1):
        if st.button(f"{opt}", key=f"stat_{idx}"):
            if opt.startswith('1'):
                p.max_hp += 4
                p.hp += 4
            elif opt.startswith('2'):
                p.attack += 1
            elif opt.startswith('3'):
                p.max_mana += 5
                p.mana += 5
            elif opt.startswith('4'):
                p.spell_power += 1
            p.stat_points -= 1
            log(f"Allocated {opt}. Stat points left: {p.stat_points}")


def show_quests_ui():
    p = st.session_state.player
    if not p:
        return
    st.subheader("Quest Log")
    for quest in p.quests:
        status = "✓" if quest.get('completed') else f"{quest.get('progress',0)}/{quest.get('goal')}"
        st.write(f"{quest['name']} - {quest['desc']} ({status})")


# UI
init_state()

st.title("LitRPG - Streamlit Prototype")

col1, col2 = st.columns([2,3])

# Left column: player panel (improved visuals, spells & skills)
with col1:
    st.header("Player")
    if not st.session_state.player:
        name = st.text_input("Name")
        roles = list(CLASS_DEFS.keys())
        role = st.selectbox("Class", roles)
        if st.button("Create Player"):
            if not name.strip():
                st.warning("Enter a name")
            else:
                create_player(name.strip(), role)
    else:
        p = st.session_state.player
        # Top metrics row
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Level", p.level)
        m_col2.metric("HP", f"{p.hp}/{p.max_hp}", delta=f"{p.hp - p.max_hp}")
        m_col3.metric("Mana", f"{p.mana}/{p.max_mana}" if p.max_mana > 0 else "N/A")
        m_col4.metric("Gold", p.gold)

        # HP/Mana progress bars
        st.progress(max(0.0, min(1.0, p.hp / max(1, p.max_hp))))
        if p.max_mana > 0:
            st.caption(f"Mana: {p.mana}/{p.max_mana}")

        st.write(f"Attack: {p.attack}  |  Spell Power: {p.spell_power}")
        st.write(f"XP: {p.xp}  |  Stat Points: {p.stat_points}")

        st.markdown("---")
        # Spells UI
        spells = SPELLS.get(p.role, []) or p.spell_list
        if spells:
            st.subheader("Spells")
            spell_cols = st.columns(len(spells))
            for i, sp in enumerate(spells):
                with spell_cols[i]:
                    st.markdown(f"**{sp['name']}**")
                    st.write(sp.get('description', ''))
                    cost = sp.get('cost', 0)
                    ctype = sp.get('cost_type', 'mana')
                    st.write(f"Cost: {cost} {ctype}")
                    if st.button(f"Cast {sp['name']}", key=f"cast_{sp['name']}"):
                        # affordability
                        can_cast = True
                        if sp.get('cost_type') == 'mana' and p.mana < cost:
                            can_cast = False
                        if sp.get('cost_type') == 'hp' and p.hp <= cost:
                            can_cast = False
                        if not can_cast:
                            log("You can't afford that spell.")
                        else:
                            # apply simple effects; target first enemy if present
                            if st.session_state.encounter and st.session_state.encounter.get('enemies'):
                                target = st.session_state.encounter['enemies'][0]
                                if sp['effect'] == 'fireball':
                                    dmg = p.spell_power + p.attack
                                    target.hp -= dmg
                                    p.mana -= cost
                                    log(f"You cast Fireball for {dmg} damage on {target.name}!")
                                elif sp['effect'] == 'eldritch_blast':
                                    dmg = p.spell_power + p.attack + random.randint(1,5)
                                    target.hp -= dmg
                                    p.mana -= cost
                                    log(f"You cast Eldritch Blast for {dmg} damage on {target.name}!")
                                elif sp['effect'] == 'hellfire':
                                    dmg = p.spell_power + p.attack + 15
                                    target.hp -= dmg
                                    p.hp -= cost
                                    log(f"You use Hellfire for {dmg} damage on {target.name} at the cost of {cost} HP!")
                                else:
                                    target.hp -= p.attack
                                    log(f"You cast {sp['name']}.")
                                end_step()
                            else:
                                log("No target to cast the spell on.")
                        rerun_safe()
        else:
            st.write("No spells available for your class yet.")

        st.markdown("---")
        # Skills UI
        if p.skill_list:
            st.subheader("Skills")
            for sk in p.skill_list:
                cd = p.skill_cooldowns.get(sk['name'], 0)
                cols = st.columns([3,1])
                with cols[0]:
                    st.write(f"**{sk['name']}** — {sk.get('description','')}")
                    st.caption(f"Cooldown: {cd} turns")
                with cols[1]:
                    disabled = cd > 0
                    if st.button(sk['name'], key=f"skill_btn_{sk['name']}", disabled=disabled):
                        # apply skill targeting first enemy if any
                        if not st.session_state.encounter or not st.session_state.encounter.get('enemies'):
                            log("No enemies to use the skill on.")
                        else:
                            use_player_skill(sk['name'], 0)
                        rerun_safe()
        else:
            st.write("No class skills.")

        st.markdown("---")
        # Quick actions
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Explore"):
                start_explore()
                rerun_safe()
        with c2:
            if st.button("Open Shop"):
                open_shop_ui()
                rerun_safe()
        with c3:
            if st.button("View Quests"):
                show_quests_ui()

# Right column: encounter (improved visuals)
with col2:
    st.header("Encounter")
    if st.session_state.encounter is None:
        st.write("No active encounter. Click Explore to find foes.")
    else:
        enc = st.session_state.encounter
        enemies = enc['enemies']
        # Show each enemy as a card with actions
        for idx, e in enumerate(list(enemies)):
            card_cols = st.columns([3,2,2,1])
            with card_cols[0]:
                st.subheader(f"{idx+1}. {e.name}")
                st.progress(max(0.0, min(1.0, e.hp / max(1, e.hp))))
                st.write(f"HP: {e.hp}")
            with card_cols[1]:
                if st.button(f"Attack {idx}", key=f"atk_{idx}"):
                    apply_player_attack(idx)
                    rerun_safe()
            with card_cols[2]:
                # Skill quick-use dropdown
                if st.session_state.player and st.session_state.player.skill_list:
                    sk_list = [s['name'] for s in st.session_state.player.skill_list]
                    sel = st.selectbox(f"Skill target {idx}", sk_list, key=f"sel_skill_{idx}")
                    if st.button(f"Use Skill on {idx}", key=f"use_skill_{idx}"):
                        use_player_skill(sel, idx)
                        rerun_safe()
            with card_cols[3]:
                if st.button(f"Target {idx}"):
                    # just a helper to focus target (no-op placeholder)
                    log(f"Targeting {e.name}")
                    rerun_safe()

        # Global encounter actions
        g1, g2, g3 = st.columns(3)
        with g1:
            if st.button("Attempt Escape"):
                attempt_escape()
                rerun_safe()
        with g2:
            if st.button("Use Item"):
                # open inventory first item
                if st.session_state.player and st.session_state.player.inventory:
                    item = st.session_state.player.inventory.pop(0)
                    log(f"Used {item} from inventory.")
                    end_step()
                    rerun_safe()
                else:
                    log("No item to use.")
        with g3:
            if st.button("Surrender"):
                st.session_state.player.hp = 0
                log("You surrendered.")
                reset_encounter()
                rerun_safe()

st.sidebar.header("Log")
for msg in st.session_state.log[-20:]:
    st.sidebar.write(msg)


# Footer note
st.write("\n---\nPrototype: Streamlit UI wired to core Player/Enemy/skills. This is minimal and intended as a starting point.")
