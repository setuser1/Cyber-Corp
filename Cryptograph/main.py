import crypto
import random

mixkey = crypto.main()  # Assuming this returns an integer



characters = [
        # Uppercase letters
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        
        # Lowercase letters
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        
        # Digits
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        
        # Basic specials
        '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/',
        ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~',
]

total = 0
mixkey = list(str(mixkey))
for i in mixkey:
        total += int(i)

total = total % len(characters)
text = input("Enter the text to be encrypted: ")
for i in range(total):        
        random.shuffle(characters)  # Shuffle the characters based on the seed
text.split()
text = list(text)  # Convert the text to a list of characters
for i in text:
        if i in characters:
                index = characters.index(i)
                new_index = (index + total) % len(characters)
                text[text.index(i)] = characters[new_index]
print("Encrypted text:", ''.join(text))  # Join the list back into a string for output

