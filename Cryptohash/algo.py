import random
from crypto import mixkey

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


def encode(text):
    # Set the random seed for deterministic shuffling
    random.seed(mixkey)
    shuffled_characters = characters.copy()
    random.shuffle(shuffled_characters)

    encrypted_text = []
    for char in text:
        if char in characters:
            encrypted_text.append(shuffled_characters[characters.index(char)])
        else:
            encrypted_text.append(char)  # Leave unsupported characters unchanged

    return ''.join(encrypted_text)

def decode(encrypted_text):
    # Set the same random seed to reproduce the shuffle
    random.seed(mixkey)
    shuffled_characters = characters.copy()
    random.shuffle(shuffled_characters)

    decrypted_text = []
    for char in list(encrypted_text):
        if char in shuffled_characters:
            decrypted_text.append(characters[shuffled_characters.index(char)])
        else:
            decrypted_text.append(char)  # Leave unsupported characters unchanged

    return ''.join(decrypted_text)
