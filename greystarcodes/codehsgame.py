import random #imports the random library
def game(): #defines a function
    overall_score = 0 #these variables sets all the default scores when first starting the program
    round_score = 0
    turn_num = 1
    high_score = 0
    print(f"Turn {turn_num}") #tells the user the default score values
    print(f"Your Current Score is: {overall_score}")
    print(f"This round you have: {round_score}")    
    print("Your previous highscore is 0.")
    while True: #a while loop that runs the game until the user decides to not play no more
        r_b = input("Would you like to roll or bank? ")
        if r_b == "roll" or "r": 
            roll_dice = random.randint(1,6) #rolls the dice to get a value from 1 through 6
            if roll_dice > 1:
                print(f"You rolled a {roll_dice}.")
                round_score = round_score + roll_dice #adds the score to the temporary round score
                print(f"This round you have: {round_score}")
            else:
                round_score = 0 #if the dice value is 1 the round score gets reseted
                print(f"You rolled a {roll_dice}.") 
                print(f"Your round score has been reseted You now have {round_score}.")
        elif r_b == "bank" or "b": #banking adds the score to the overall score that doesn't reset when 1 is rolled
            overall_score = overall_score + round_score
            round_score = 0
            turn_num += 1 #change the turn number when the user banks
            print(f"Turn {turn_num}") #prints all the current scores
            print(f"Your Current Score is: {overall_score}")
            print(f"This round you have: {round_score}")
            print(f"Your previous highscore is {high_score}.")
        else:
            print("Invalid Input") #if the user mistypes they will get prompted to either contiue the game or leave it
            continues = input("Do you want to continue the game? (y/n)")
            if continues == "y": #if input is y, the game continues
                continue
            elif continues == "n": #if input is no, the game is closed
                print("Thanks for playing!") 
                break
            else: #if the input is invalid, the game is automatically continued
                print("Invalid Input")
                print("The game will automatically continue.")
                continue
        if overall_score > 99: #when score is 100 or higher, the game ends
            print("You have beat the game!")
            continues = input("Do you want to start a new game? (y/n)") #prompts the user if they want to play a new game
            if continues == "y": #if yes, the game will continue
                print("Your highest score will be saved.") #highest score will be saved through if statments
                if high_score < overall_score:
                    high_score = overall_score
                elif high_score == overall_score:
                    high_score = overall_score
                else:
                    high_score = high_score
                overall_score = 0
                round_score = 0
                turn_num = 1
                print(f"Turn {turn_num}") #tells player default score
                print(f"Your Current Score is: {overall_score}")
                print(f"This round you have: {round_score}")    
                print(f"Your current highscore is {high_score}.")
                continue
            elif continues == "n": #ends game
                print("Thanks for playing!")
                print(f"Your highest score is {high_score}.")
                break
            else: #refreshes game to beginning to fix error
                print("Invalid Input")
                print("Play one more roll or bank to come back to this page.")
                continue
game() #calling the function to start the game when run
