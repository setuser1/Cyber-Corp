#made using copilot, I debugged the code shouldn't have any problems encrypting

import random

characters = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/',
    ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', ' '
]

# Set a fixed random seed for consistency
random.seed(7)

# Generate a list of unique numbers below 100
numbers = list(range(1, 100))  # Ensure all values are below 100
random.shuffle(numbers)

# Assign characters to shuffled numbers
char_to_number = {char: numbers[i] for i, char in enumerate(characters[:len(numbers)])}

# Print the result
for char, num in char_to_number.items():
    print(f"'{char}': {num}")

