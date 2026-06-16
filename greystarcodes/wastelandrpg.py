import random
import time

print("Boom! You were jolted awake by a loud, sudden noise, hurriedly scrambling to find out what had happened. \n"
      "When #$%^%&, kicked down the door and told you to head into the bunker, grabbing your hand \n"
      "and pulled you along. As you head out of your chamber, you notice soldiers fighting against an unknown group. \n"
      "#$%^%& then pulled you down an alley and pushed you into the hidden bunker below the city, \n"
      "while staying back to hold off the unknown group. \n"
      "You struggle wildly, punching and kicking as mechanical arms inside the bunker grab onto you, knocking you on the head. \n"
      "As the world around you began to lurch, you heard a voice coming from outside the bunker. 'I am sorry. This is for the best.' \n"
      "You struggle to keep your eyes open, and everything fades to black.")

#------------
#Character Classes
#------------

class Player:
    def __init__(self, name):
        self.name = name
        self.lvl = 1
        self.con = 10
        self.stg = 10
        self.agi = 12
        self.per = 11
        self.end = 10
        self.hp = 100
        self.max_hp = 100
        self.free_points = 0

    def dmg_taken(self, amount):
        self.hp = max(0, self.hp - amount)
        print(f"You have taken {amount} points of damage. Remaining hp: {self.hp}")
        
class MutantEnemy1:
    def __init__(self):
        self.name = "One-Armed Mutant"
        self.agi = 8
        self.max_hp = 60
        self.hp = 60
        self.has_smashed = False  # Tracks if the powerful single-arm attack has been used

    def choose_move(self):
        """AI Logic determining what attack the mutant uses."""
        # 1. Trigger desperation explosion if health drops below 20
        if self.hp <= 20:
            return "Explode"
        
        # 2. If it hasn't used its massive arm attack yet, 40% chance to execute it
        if not self.has_smashed and random.random() < 0.40:
            self.has_smashed = True  # Can only execute once per combat
            return "One-Arm Smash"
        
        # 3. Default attack pool if conditions aren't met
        return random.choice(["Bite", "Headbutt"])
        
    def dmg_taken(self, amount):
        self.hp = self.hp - amount
        if self.hp <= 0:
            self.hp = 0
            print(f"The mutant has been defeated! Remaining hp: {self.hp} ")
        else:    
            print(f"The mutant has taken {amount} points of damage. Remaining hp: {self.hp}")
#------------

print("\n----??? years later---- \n"
      "You wake up groggily, stepping out of a capsule. Your eyes adapt to your surrounding environment. \n"
      "When you suddenly came to a realization... what is your name?")

player_name_choice = input("Choose your name: ") #variable to get and save username

player1 = Player(player_name_choice) #saves name into a class instance

print(f"\nAfter long contemplation, you decided to call yourself {player1.name}.\nAs you finally decided on your name, a loud growling noise could be heard from down the hall. \nYou turn to look, noticing a single armed, red skinned mutant \nwith teeth that seem to be about 15 inches long.")
print(f"Just as you were recovering from the shock of seeing a mutant for the first time, it rudely began charging at you.")
print(f"You have now entered combat with the One Armed Mutant!")

def player_combat_options(mutant, value):
    if value == 1:
        #gambling is good for you, thats why your damage will be random *will change this depending on stats later on*
        dmg = random.randint(10,15) * player1.stg / 10
        mutant.dmg_taken(dmg) 
    if value == 2:
        if random.randint(2,5) * player1.agi > mutant.agi * random.randint(3,5):
            print("You successfully fled from the mutant!")
            exit()
        else:
            print("You failed to flee! The mutant attacks you!")
    else:
        print("You hesitated for too long! The mutant attacks you!")

# Create an instance of the mutant before passing it
mutant_enemy = MutantEnemy1()

while True:
    if mutant_enemy.hp <= 0:
        print("You won!")
        break
    try:
        value = int(input("\nWhat will you do? \n 1. Attack \n 2. Flee \n > "))
        player_combat_options(mutant_enemy, value)
    except ValueError:
        print("Invalid input! Please enter a number.")
        continue
