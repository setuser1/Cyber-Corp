# debugged, uses mostly the same code from MoreEncyption.py
# code below only decrypt the part from MoreEncryption.py

#haven't figured out how we're going to decrypt the number sorter thing

import random

characters = [
    #alphabet
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    #special characters
    '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-',
    '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^',
    '_', '`', '{', '|', '}', '~', ' ',
    #digits
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
]

# Set a fixed random seed for consistency
random.seed(7)

# Generate a list of unique numbers below 100
numbers = list(range(1, 100))  # Ensure all values are below 100
random.shuffle(numbers)

# Assign characters to shuffled numbers
char_to_number = {char: numbers[i] for i, char in enumerate(characters[:len(numbers)])}

# Reverse mapping: numbers back to characters
number_to_char = {num: char for char, num in char_to_number.items()}

# Get user input
encrypted_input = input("Enter encrypted numbers separated by spaces (single digits values must have a zero in front):")

# Convert input into a list of numbers
encrypted_numbers = encrypted_input.split()

# Ensure single-digit numbers have a leading zero
processed_numbers = [num.zfill(2) if len(num) == 1 else num for num in encrypted_numbers]

# Convert numbers back to characters
try:
    decrypted_text = ''.join(number_to_char[int(num)] for num in processed_numbers)
    print(decrypted_text)
except KeyError:
    print("Error: One or more numbers do not match the expected encryption pattern.")
