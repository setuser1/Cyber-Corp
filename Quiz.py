#ai generated

import os

def delete_file():
    filename = input("Enter the filename to delete: ")
    if os.path.exists(filename):
        confirm = input(f"Are you sure you want to delete '{filename}'? (yes/no): ").strip().lower()
        if confirm == "yes":
            os.remove(filename)
            print(f"File '{filename}' deleted successfully!\n")
        else:
            print("File deletion canceled.\n")
    else:
        print("File does not exist.\n")

def load_quiz(filename):
    quiz = []
    if os.path.exists(filename):
        with open(filename, "r") as file:
            lines = file.readlines()
            for line in lines:
                question, answer = line.strip().split("|")
                quiz.append((question, answer))
    return quiz

def get_quiz_input():
    quiz = []
    print("Enter your quiz questions and answers. Type 'done' when finished.")
    while True:
        question = input("Enter question: ")
        if question.lower() == "done":
            break
        answer = input("Enter answer: ")
        quiz.append((question, answer))
    return quiz

def save_to_file(quiz):
    filename = input("Enter the filename to save the quiz (e.g., quiz.txt): ")
    
    if os.path.exists(filename):
        choice = input(f"The file '{filename}' exists. Do you want to append to it? (yes/no): ").strip().lower()
        mode = "a" if choice == "yes" else "w"
    else:
        mode = "w"

    with open(filename, mode) as file:
        for question, answer in quiz:
            file.write(f"{question}|{answer}\n")
    
    print(f"Quiz saved to {filename} successfully!\n")

def run_quiz(quiz):
    print("\nStarting Quiz!\n")
    score = 0
    for question, answer in quiz:
        user_answer = input(f"{question}\nYour answer: ")
        if user_answer.strip().lower() == answer.lower():
            print("Correct!\n")
            score += 1
        else:
            print(f"Wrong! The correct answer is: {answer}\n")
    
    print(f"Quiz Complete! Your score: {score}/{len(quiz)}")

def main():
    delete_choice = input("Do you want to delete a quiz file before proceeding? (yes/no): ").strip().lower()
    if delete_choice == "yes":
        delete_file()

    choice = input("Do you want to open an existing quiz file? (yes/no): ").strip().lower()

    if choice == "yes":
        filename = input("Enter the filename of the existing quiz: ")
        if os.path.exists(filename):
            quiz = load_quiz(filename)
        else:
            print("File does not exist. Exiting.")
            return
    else:
        quiz = get_quiz_input()
        save_to_file(quiz)

    run_quiz(quiz)

if __name__ == "__main__":
    main()
