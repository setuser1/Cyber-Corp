#made using copilot, I debugged the code and haven't found any other bugs in the code

import random

characters = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    
    '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-',
    '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^',
    '_', '`', '{', '|', '}', '~', ' ',
    
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
]

# Set a fixed random seed for consistency
random.seed(7)

# Generate a list of unique numbers below 100
numbers = list(range(1, 100))  # Ensure all values are below 100
random.shuffle(numbers)

# Assign characters to shuffled numbers
char_to_number = {char: numbers[i] for i, char in enumerate(characters[:len(numbers)])}

# Get user input
user_text = input("Enter text to encrypt: ")

# Encrypt the input text
encrypted_numbers = [str(char_to_number[char]) if char in char_to_number else '?' for char in user_text]

# Output encrypted message without space after ":"
print("Encrypted text:" + ' '.join(encrypted_numbers))
