# mostly debugged

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
