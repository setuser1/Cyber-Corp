#ai generated
#version 2
#untested

import os

def list_files():
    print("\nSupported quiz filenames must end in: .quiz, .txt, .csv, or .json")
    
    files = [f for f in os.listdir() if f.endswith((".quiz", ".txt", ".csv", ".json"))]
    
    if files:
        print("\nAvailable quiz files:")
        for idx, file in enumerate(files, start=1):
            print(f"{idx}. {file}")  
    else:
        print("\nNo quiz files found.\n")

def delete_file():
    list_files()  
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
        with open(filename, "r", encoding="utf-8") as file:  
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split("|")
                if len(parts) == 2:  # Ensure correct format
                    question, answer = parts
                    quiz.append((question, answer))
                else:
                    print(f"Warning: Skipping invalid line -> {line.strip()}")
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

def save_to_file(quiz, filename, mode):
    with open(filename, mode, encoding="utf-8") as file:  
        for question, answer in quiz:
            file.write(f"{question}|{answer}\n")
    
    print(f"Quiz saved to {filename} successfully!\n")

def run_quiz(quiz):
    if not quiz:  # Prevents running an empty quiz
        print("This quiz is empty. No questions to ask!")
        return
    
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

    file_choice = input("Do you want to add to an existing quiz file or create a new one? (existing/new): ").strip().lower()
    
    if file_choice == "existing":
        list_files()  
        filename = input("Enter the filename of the existing quiz: ")
        if os.path.exists(filename):
            quiz = load_quiz(filename)
            add_more = input("Do you want to add new questions to this quiz? (yes/no): ").strip().lower()
            if add_more == "yes":
                quiz.extend(get_quiz_input())
                save_to_file(quiz, filename, "w")
        else:
            print("File does not exist. Exiting.")
            return
    elif file_choice == "new":
        filename = input("Enter the filename for your new quiz (including extension, e.g., quiz.txt): ")
        if "." not in filename:  # Ensure extension is added
            filename += ".txt"
        
        if os.path.exists(filename):
            confirm = input(f"Warning: '{filename}' already exists. Overwrite? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("File creation canceled.")
                return
        
        quiz = get_quiz_input()
        save_to_file(quiz, filename, "w")
    else:
        print("Invalid option. Exiting.")
        return

    run_quiz(quiz)

if __name__ == "__main__":
    main()
